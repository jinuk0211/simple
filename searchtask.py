from prompt import *
import re
import os

class SearchTask(object):
    def __init__(self, data, model, processor, propose_method='qwen', value_method='glm'):
        super().__init__()
        self.question = data
        self.model = model
        self.processor = processor
        # self.clip = clip
        # self.clip_processor = clip_processor
        # self.llm = llm
        # self.tokenizer = tokenizer
        self.propose_method = propose_method
        self.value_method = value_method
        self.value_cache = {}

    def clear_cache(self):
        self.value_cache = {}

    @staticmethod
    def image_description_score(x,y):
        print('\n', '==============================', 'image description score', '==============================', '\n')
        prompt = image_description_score + x 
        return prompt
    @staticmethod
    def image_description(x,y):
        print('\n', '==============================', 'image description', '==============================', '\n')
        image_description_prompt = '''
        Your task is to provide the image description based on a given image and corresponding problem,
        The output format is limited to:
        "Image Description:..."
        where ... represents the omitted output information, which you should fill in.

        Given problem: '''
        prompt = image_description_prompt + x
        return prompt        
    @staticmethod
    def llm_prompt(x,y):

        prompt = llm_prompt + x + y
        return prompt
    @staticmethod
    def summary_prompt_wrap(x: str, y: str = '') -> str:
        summary_prompt = '''
        Your task is to summarize the final answer in one sentence based on a given science/math problem and its completed solution steps, following the specified format.

        Given problem: '''
        print('\n', '==============================', 'summary', '==============================', '\n')
        print('summary_prompt: \n', x + '\nexisting step:\n' + y + 'The summary based on the reasoning steps i:\n')
        prompt = summary_prompt + x + '\nexisting step:\n' + y + '\noutput:'
        return prompt

    @staticmethod
    def MATH_summary_prompt_wrap(x: str, y: str = '') -> str:
        MATH_summary_prompt = '''
        Given a problem, image, image description and its corresponding solution, your task is to extract the final answer obtained in the solution.
        You should summarize the answer using the format: "The final answer is $...$". Replace "..." with the answer obtained in the solution.
        Problem: '''

        print('\n', '==============================', 'summary', '==============================', '\n')
        print('math_summary_prompt: \n', x + '\nexisting step:\n' + y + 'The summary based on the reasoning steps i:\n')
        prompt = MATH_summary_prompt + x + '\nSolution: ' + y + '\nExtracted answer:'
        return prompt


    @staticmethod
    def general_evaluate_summary_prompt_wrap(x: str, y: str = '') -> str:
        general_evaluate_summary_prompt = '''
        Your task is to provide the final answer based on a given problem and the existing solution steps, following the specified format in the problem.
        Below are a few examples for you to learn from.

        Given problem:'''

        print('\n', '==============================', 'summary', '==============================', '\n')
        print('general_summary_prompt: \n', x + '\nexisting step:\n' + y + 'The summary based on the reasoning steps i:\n')
        prompt = general_evaluate_summary_prompt + x + '\nexisting step:\n' + y + '\noutput:'
        return prompt

    # Example 1
    # Problem: Determine for which values of p the generalized integral \( \int_0^{+\infty} \frac{x^p \ln x}{(1+x^2)^2}dx \) converges.
    # Image description:
    # Given steps:
    # Step 1: Consider the necessary and sufficient conditions for the convergence of the integral: Let \( J = \int_0^{+\infty} \frac{x^p \ln x}{(1+x^2)^2}dx \), \( J_1 = \int_0^{1} \frac{x^p \ln x}{(1+x^2)^2}dx \), \( J_2 = \int_1^{+\infty} \frac{x^p \ln x}{(1+x^2)^2}dx \). Then, the generalized integral \( J \) converges if and only if both \( J_1 \) and \( J_2 \) converge.

    # Output:
    # Analysis: The convergence of the generalized integral is determined by the integrals over its subintervals. According to Step 1, we have decomposed the original integral into two parts, \( J_1 \) and \( J_2 \). To determine the convergence of \( J \), we need to analyze these two parts separately. For \( J_1 \), within the interval \([0,1]\), specific behavior occurs as \( x \) approaches 0, so we need to study its behavior as \( x \) approaches 0. For \( J_2 \), the focus is on the behavior as \( x \) approaches \( +\infty \).
    # Next step: To analyze the convergence of \( J_1 \), compare it with a known function (such as \( x^a \ln x \) where \( a > -1 \) is convergent) as \( x \to 0^+ \). Specifically, we can choose an appropriate \( q \) such that when \( p > q \), \( \frac{x^p \ln x}{(1+x^2)^2} > x^q \ln x \), thereby deducing the convergence of \( J_1 \).



    @staticmethod
    def single_propose_prompt_wrap(x: str, y: str = '', step: int = 0) -> str:
        print('\n', '==============================', 'single_propose_prompt_wrap', '==============================', '\nstep: ', step)
        print('single_propose_prompt: \n', x + '\nexisting step:\n' + y + 'Based on the steps outlined earlier, a possible solution for the current step is:\n')
        prompt = single_proposal_prompt + x + '\nexisting step:\n' + y + '\noutput:'
        return prompt


    @staticmethod
    def zero_single_propose_wrap(x: str, y: str = '', step: int = 0, lang: str = 'zh') -> str:
        print('\n', '==============================', 'zero_single_propose_wrap', '==============================', '\nstep: ', step)
        print('zero_propose_prompt: \n', x + '\nexisting step:\n' + y + 'Based on the steps outlined earlier, a possible solution for the current step is:\n')
        if not y:
            y = 'None\n'
        prompt = zero_single_proposal_prompt_en + x + '\nExisting Steps:\n' + y + '\nOutput:'
        return prompt


   

    # @staticmethod
    # def single_reflection_wrap(x: str, y: str = '', step: int = 0, lang: str = 'zh') -> str:
    #     print('\n', '==============================', 'single_reflection_wrap', '==============================', '\nstep: ', step)
    #     print('reflection_prompt: \n', x + '\nexisting step:\n' + y + '基于以上步骤给出的意见:\n')

    #     if not y:
    #         y = 'None\n'
    #     prompt = single_reflection_prompt_en + x + '\nExisting Steps:\n' + y + '\nOutput:'
    #     return prompt


    @staticmethod
    def single_reflection_wrap_simple(x: str, y: str = '', step: int = 0, lang: str = 'en') -> str:
        print('\n', '==============================', 'single_reflection_wrap_simple', '==============================', '\nstep: ', step)
        print('propose_prompt: \n', x + '\nexisting step:\n' + y + '基于以上步骤给出的意见:\n')
        if lang == 'en':
            if not y:
                y = 'None\n'
            prompt = single_reflection_prompt_simple_en + x + '\nExisting Steps:\n' + y
        return prompt

    @staticmethod
    def value_prompt_wrap(x: str, y: str) -> str:
        print('\n', '==============================', 'value_prompt', '==============================', '\n')
        value_prompt = critic_simplified + x + '\nexisting step:\n' + y.strip() + '\noutput:'
        return value_prompt



    @staticmethod
    def value_outputs_unwrap(value_outputs, low=0.0, high=1.0) -> float:
        out_value = low
        print(f'value_unwrap 안되는 이유:{value_outputs,type(value_outputs)}')
        if 'Score' not in value_outputs:
            print('점수 출력이 올바르지 않습니다 value_outputs_unwrap\n')
        try:
            out_value = float(value_outputs.split(":")[-1].strip())
            out_value = min(max(low, out_value), high)
        except Exception as e:
            print(f'점수 출력에 오류가 있습니다! 오류 유형:{e}\n')
            return low
        print(f'최종:{out_value,type(out_value)}')
        return out_value
