from flask import Flask, render_template, request, jsonify
import re
import random
import os

app = Flask(__name__)

# 添加chr函数到Jinja2环境
app.jinja_env.globals.update(chr=chr)

# 全局变量存储题目和当前题号
questions = []
current_question_index = 0

def parse_questions(file_path):
    """解析题库文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 正则表达式匹配题目格式
        pattern = r'\[Q\](.+?)\nA\.(.+?)\nB\.(.+?)\nC\.(.+?)\nD\.(.+?)(?=\n\n\[Q\]|\Z)'
        questions_raw = re.findall(pattern, content, re.DOTALL)
        
        parsed_questions = []
        for q in questions_raw:
            # 去除每个选项的首尾空白
            options = [opt.strip() for opt in q[1:5]]
            parsed_questions.append({
                'question': q[0].strip(),
                'options': options,
                'correct_answer': options[0]  # 第一个选项是正确答案
            })
        
        print(f"成功解析 {len(parsed_questions)} 道题目")
        return parsed_questions
        
    except Exception as e:
        print(f"解析题库出错: {str(e)}")
        return []

@app.route('/')
def index():
    """首页路由，显示当前题目"""
    global questions, current_question_index
    
    try:
        # 首次访问时加载题库
        if not questions:
            questions = parse_questions('无线电A类题库-记事本版.txt')
            if not questions:
                return render_template('error.html', message="题库解析失败，请检查题库文件格式！")
            random.shuffle(questions)
            current_question_index = 0
        
        # 获取当前题目
        question = questions[current_question_index]
        
        # 复制并打乱选项顺序
        shuffled_options = question['options'].copy()
        random.shuffle(shuffled_options)
        
        # 确定正确答案的位置
        correct_letter = chr(65 + shuffled_options.index(question['correct_answer']))
        
        return render_template(
            'quiz.html',
            question_text=question['question'],
            options=shuffled_options,
            question_number=current_question_index + 1,
            total_questions=len(questions),
            correct_answer=correct_letter
        )
        
    except Exception as e:
        print(f"首页加载错误: {str(e)}")
        return render_template('error.html', message=f"系统错误：{str(e)}")

@app.route('/navigate', methods=['POST'])
def navigate():
    """导航到上一题或下一题"""
    global current_question_index
    
    try:
        direction = request.form.get('direction')
        if not direction:
            raise ValueError("缺少direction参数")
        
        # 更新当前题号
        if direction == 'next' and current_question_index < len(questions) - 1:
            current_question_index += 1
        elif direction == 'prev' and current_question_index > 0:
            current_question_index -= 1
        
        # 返回更新后的题目
        return index()
        
    except Exception as e:
        print(f"导航出错: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/check_answer', methods=['POST'])
def check_answer():
    """检查答案是否正确"""
    try:
        selected = request.form.get('answer')
        correct = request.form.get('correct_answer')
        
        if not selected or not correct:
            raise ValueError("缺少答案参数")
        
        is_correct = selected == correct
        
        return jsonify({
            'correct': is_correct,
            'message': '回答正确！' if is_correct else f'回答错误，正确答案是 {correct}'
        })
        
    except Exception as e:
        print(f"检查答案出错: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # 确保模板文件夹存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, port=5001)