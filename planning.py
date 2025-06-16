from pocket import *
import asyncio
import json
import re
from gemini import llm_response
from pprint import pprint

class TaskAnalysisNode(AsyncNode):
    """分析用户输入的任务，提取关键信息"""
    
    async def prep_async(self, shared):
        return shared.get('user_input', '')
    
    async def exec_async(self, user_input):
        prompt = f"""
        请分析以下用户任务，提取关键信息：
        用户输入：{user_input}
        
        请以JSON格式返回分析结果，包含：
        - task_type: 任务类型（如：数据处理、文本分析、图像处理等）
        - complexity: 复杂度（简单/中等/复杂）
        - required_steps: 需要的主要步骤列表
        - dependencies: 步骤间的依赖关系
        - estimated_time: 预估时间
        
        只返回JSON，不要其他文字，不要包含开头的标记```json。
        示例返回格式：

        {{
            "task_type": "数据处理",
            "complexity": "中等",
            "required_steps": ["数据清洗", "特征提取", "模型训练"],
            "dependencies": ["数据清洗 -> 特征提取", "特征提取 -> 模型训练"],
            "estimated_time": "2小时"
        }}
        """
        
        response = llm_response([{'role': 'user', 'content': prompt}]).strip()
        if response.startswith('```json'):
            response = response.split('```json')[1].strip()
        if response.endswith('```'):
            response = response[:-3].strip()
        try:
            return json.loads(response)
        except:
            # 如果解析失败，返回默认结构
            return {
                "task_type": "通用任务",
                "complexity": "中等",
                "required_steps": ["分析输入", "处理数据", "生成结果"],
                "dependencies": [],
                "estimated_time": "未知"
            }
    
    async def post_async(self, shared, prep_res, exec_res):
        shared['task_analysis'] = exec_res
        return exec_res

class WorkflowPlanningNode(AsyncNode):
    """根据任务分析结果规划具体的工作流"""
    
    async def prep_async(self, shared):
        return shared.get('task_analysis', {})
    
    async def exec_async(self, task_analysis):
        prompt = f"""
        基于以下任务分析，设计一个详细的工作流：
        {json.dumps(task_analysis, ensure_ascii=False, indent=2)}
        
        请设计具体的工作流步骤，以JSON格式返回：
        {{
            "workflow_name": "工作流名称",
            "steps": [
                {{
                    "step_id": "step_1",
                    "name": "步骤名称",
                    "description": "步骤描述",
                    "type": "数据处理/API调用/文件操作等",
                    "params": {{"参数名": "参数值"}},
                    "next_steps": ["step_2"],
                    "condition": "执行条件（可选）"
                }}
            ],
            "start_step": "step_1"
        }}
        
        只返回JSON，不要其他文字。
        """
        
        response = llm_response([{'role': 'user', 'content': prompt}]).strip()
        if response.startswith('```json'):
            response = response.split('```json')[1].strip()
        if response.endswith('```'):
            response = response[:-3].strip()
        try:
            return json.loads(response)
        except:
            return {
                "workflow_name": "默认工作流",
                "steps": [
                    {
                        "step_id": "step_1",
                        "name": "处理输入",
                        "description": "处理用户输入",
                        "type": "数据处理",
                        "params": {},
                        "next_steps": [],
                        "condition": None
                    }
                ],
                "start_step": "step_1"
            }
    
    async def post_async(self, shared, prep_res, exec_res):
        shared['workflow_plan'] = exec_res
        return exec_res

class DynamicStepNode(AsyncNode):
    """动态执行步骤的通用节点"""
    
    def __init__(self, step_config):
        super().__init__()
        self.step_config = step_config
    
    async def prep_async(self, shared):
        return {
            'step_config': self.step_config,
            'shared_data': shared,
            'user_input': shared.get('user_input', '')
        }
    
    async def exec_async(self, prep_data):
        step_config = prep_data['step_config']
        step_type = step_config.get('type', '数据处理')
        
        # 根据步骤类型执行不同的逻辑
        if step_type == '数据处理':
            return await self._process_data(prep_data)
        elif step_type == 'API调用':
            return await self._api_call(prep_data)
        elif step_type == '文件操作':
            return await self._file_operation(prep_data)
        elif step_type == '文本分析':
            return await self._text_analysis(prep_data)
        else:
            return await self._generic_processing(prep_data)
    
    async def _process_data(self, prep_data):
        # 数据处理逻辑
        step_config = prep_data['step_config']
        user_input = prep_data['user_input']
        
        prompt = f"""
        执行数据处理步骤：
        步骤名称：{step_config['name']}
        步骤描述：{step_config['description']}
        用户输入：{user_input}
        参数：{step_config.get('params', {})}
        
        请处理这个步骤并返回结果。
        """
        
        return llm_response([{'role': 'user', 'content': prompt}])
    
    async def _api_call(self, prep_data):
        # API调用逻辑
        return f"执行API调用：{prep_data['step_config']['name']}"
    
    async def _file_operation(self, prep_data):
        # 文件操作逻辑
        return f"执行文件操作：{prep_data['step_config']['name']}"
    
    async def _text_analysis(self, prep_data):
        # 文本分析逻辑
        step_config = prep_data['step_config']
        user_input = prep_data['user_input']
        
        prompt = f"""
        执行文本分析：
        分析目标：{step_config['description']}
        文本内容：{user_input}
        
        请进行详细分析并提供结果。
        """
        
        return llm_response([{'role': 'user', 'content': prompt}])
    
    async def _generic_processing(self, prep_data):
        # 通用处理逻辑
        step_config = prep_data['step_config']
        
        prompt = f"""
        执行通用处理步骤：
        步骤：{step_config['name']} - {step_config['description']}
        输入数据：{prep_data['user_input']}
        
        请处理并返回结果。
        """
        
        return llm_response([{'role': 'user', 'content': prompt}])
    
    async def post_async(self, shared, prep_res, exec_res):
        step_id = self.step_config['step_id']
        if 'step_results' not in shared:
            shared['step_results'] = {}
        shared['step_results'][step_id] = exec_res
        
        # 根据条件决定下一步
        next_steps = self.step_config.get('next_steps', [])
        if next_steps:
            return next_steps[0]  # 简单情况下返回第一个下一步
        return None

class WorkflowExecutionFlow(AsyncFlow):
    """动态构建并执行工作流"""
    
    async def prep_async(self, shared):
        workflow_plan = shared.get('workflow_plan', {})
        return workflow_plan
    
    async def _build_dynamic_workflow(self, workflow_plan):
        """根据规划动态构建工作流节点"""
        steps = workflow_plan.get('steps', [])
        start_step_id = workflow_plan.get('start_step', '')
        
        # 创建节点映射
        nodes = {}
        for step in steps:
            node = DynamicStepNode(step)
            nodes[step['step_id']] = node
        
        # 连接节点
        for step in steps:
            current_node = nodes[step['step_id']]
            next_steps = step.get('next_steps', [])
            
            for next_step_id in next_steps:
                if next_step_id in nodes:
                    current_node >> nodes[next_step_id]
        
        # 设置起始节点
        if start_step_id in nodes:
            self.start(nodes[start_step_id])
        
        return nodes
    
    async def _orch_async(self, shared, params=None):
        workflow_plan = shared.get('workflow_plan', {})
        await self._build_dynamic_workflow(workflow_plan)
        return await super()._orch_async(shared, params)

class AIAgentPlanningFlow(AsyncFlow):
    """主工作流：AI Agent规划系统"""
    
    def __init__(self):
        super().__init__()
        
        # 构建主工作流
        task_analysis = TaskAnalysisNode()
        workflow_planning = WorkflowPlanningNode()
        workflow_execution = WorkflowExecutionFlow()
        
        # 连接节点
        task_analysis >> workflow_planning >> workflow_execution
        
        # 设置起始节点
        self.start(task_analysis)
    
    async def post_async(self, shared, prep_res, exec_res):
        # 整理最终结果
        result = {
            'user_input': shared.get('user_input', ''),
            'task_analysis': shared.get('task_analysis', {}),
            'workflow_plan': shared.get('workflow_plan', {}),
            'step_results': shared.get('step_results', {}),
            'final_result': exec_res
        }
        return result

# 使用示例
async def run_ai_agent(user_input):
    """运行AI Agent规划系统"""
    shared_data = {'user_input': user_input}
    
    # 创建并运行工作流
    agent_flow = AIAgentPlanningFlow()
    result = await agent_flow.run_async(shared_data)
    
    return result

# 测试函数
async def test_planning():
    user_inputs = [
        "调查tesla的市场表现和用户反馈",
    ]
    
    for user_input in user_inputs:
        print(f"\n=== 处理任务：{user_input} ===")
        result = await run_ai_agent(user_input)
        
        print(f"任务分析：{result['task_analysis']}")
        print(f"工作流规划：{result['workflow_plan']['workflow_name']}")
        print(f"执行结果：{result['final_result']}")

if __name__ == "__main__":
    # 运行测试，先测试单个节点
    # test1 = TaskAnalysisNode()
    # shared_data = {'user_input': "调查tesla的市场表现和用户反馈"}
    # asyncio.run(test1.run_async(shared_data))
    # test2 = WorkflowPlanningNode()
    # asyncio.run(test2.run_async(shared_data))
    # for step in shared_data.get('workflow_plan', {}).get('steps', []):
    #     print('--- 步骤信息 ---')
    #     print(f'{step["step_id"]}: {step["name"]} - {step["description"]}')
    # pprint(shared_data['workflow_plan'])

    # 运行完整的AI Agent规划系统
    asyncio.run(test_planning())