# simple_ime_gui_paged.py

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
import re

pinyin_dict = {
    'zhong1': ['中', '忠', '终', '钟', '仲', '众', '肿', '冢', '踵', '螽', '种'],
    'guo2': ['国', '果', '过', '锅', '郭', '裹', '帼'],
    'zhong1 guo2': ['中国'],
    'ren2': ['人', '仁', '忍'],
    'min2': ['民', '敏', '闽'],
    'ren2 min2': ['人民'],
    'zhong': ['中'],
    'guo': ['国'],
    'zhong guo': ['中国'],
    'ren': ['人'],
    'min': ['民'],
    'ren min': ['人民'],
}

def split_pinyin_with_tone(input_str, pinyin_set):
    result = []
    pattern = re.compile(r'[a-z]+[1-4]?')

    def dfs(start, path):
        if start == len(input_str):
            result.append(path)
            return
        for end in range(start + 1, len(input_str) + 1):
            segment = input_str[start:end]
            if pattern.fullmatch(segment) and segment in pinyin_set:
                dfs(end, path + [segment])

    dfs(0, [])
    return result

def get_candidates(pinyin_list):
    joined = ' '.join(pinyin_list)
    return pinyin_dict.get(joined, [])

class IMEWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("拼音输入法（支持分页）")
        self.init_ui()

        # 分页相关
        self.current_candidates = []
        self.current_page = 0
        self.candidates_per_page = 9

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("请输入拼音（带声调如 zhong1guo2）：")
        layout.addWidget(self.label)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        self.convert_btn = QPushButton("转换")
        self.convert_btn.clicked.connect(self.process_input)
        layout.addWidget(self.convert_btn)

        self.candidates_label = QLabel("候选词：")
        layout.addWidget(self.candidates_label)

        self.result_label = QLabel("上屏结果：")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def process_input(self):
        user_input = self.input_field.text().strip().lower()
        if not user_input:
            QMessageBox.warning(self, "提示", "请输入拼音！")
            return

        all_pinyins = set(pinyin_dict.keys())
        splits = split_pinyin_with_tone(user_input, all_pinyins)
        if not splits:
            self.candidates_label.setText("候选词：无法识别拼音组合。")
            return

        selected = splits[0]
        self.current_candidates = get_candidates(selected)
        self.current_page = 0
        self.refresh_candidate_display()

    def refresh_candidate_display(self):
        self.clear_candidate_widgets()

        if not self.current_candidates:
            self.candidates_label.setText("候选词：未找到对应词语。")
            return

        self.candidates_label.setText("候选词：")

        start = self.current_page * self.candidates_per_page
        end = start + self.candidates_per_page
        page_candidates = self.current_candidates[start:end]

        cand_layout = QHBoxLayout()
        for idx, word in enumerate(page_candidates):
            btn = QPushButton(f"{idx + 1}. {word}")
            btn.clicked.connect(lambda _, w=word: self.select_candidate(w))
            cand_layout.addWidget(btn)

        # 翻页按钮
        nav_layout = QHBoxLayout()
        if self.current_page > 0:
            prev_btn = QPushButton("← 上一页")
            prev_btn.clicked.connect(self.prev_page)
            nav_layout.addWidget(prev_btn)

        if end < len(self.current_candidates):
            next_btn = QPushButton("下一页 →")
            next_btn.clicked.connect(self.next_page)
            nav_layout.addWidget(next_btn)

        wrapper = QWidget()
        wrapper.setLayout(cand_layout)
        nav_wrapper = QWidget()
        nav_wrapper.setLayout(nav_layout)

        self.layout().insertWidget(4, wrapper)
        self.layout().insertWidget(5, nav_wrapper)

        self.current_candidate_widget = wrapper
        self.current_nav_widget = nav_wrapper

    def select_candidate(self, word):
        self.result_label.setText(f"上屏结果：{word}")

    def clear_candidate_widgets(self):
        for attr in ['current_candidate_widget', 'current_nav_widget']:
            if hasattr(self, attr):
                widget = getattr(self, attr)
                self.layout().removeWidget(widget)
                widget.deleteLater()
                delattr(self, attr)

    def next_page(self):
        self.current_page += 1
        self.refresh_candidate_display()

    def prev_page(self):
        self.current_page -= 1
        self.refresh_candidate_display()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = IMEWindow()
    window.resize(500, 280)
    window.show()
    sys.exit(app.exec_())
