import tkinter as tk

class DraggableRectangle:
    def __init__(self, canvas, x1, y1, x2, y2, color="red"):
        self.canvas = canvas
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        self.canvas.tag_bind(self.rect, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rect, "<B1-Motion>", self.on_drag)

        self.x = 0
        self.y = 0

    def on_press(self, event):
        # 记录点击位置的初始坐标
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        # 计算光标移动的距离
        dx = event.x - self.x
        dy = event.y - self.y
        # 移动矩形
        self.canvas.move(self.rect, dx, dy)
        # 更新点击位置
        self.x = event.x
        self.y = event.y

class RectangleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Draggable Rectangles")
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack()

        self.button = tk.Button(root, text="Create Rectangle", command=self.create_rectangle)
        self.button.pack()

    def create_rectangle(self):
        # 随机生成矩形的位置和尺寸
        x1, y1 = 50, 50
        x2, y2 = x1 + 100, y1 + 50
        DraggableRectangle(self.canvas, x1, y1, x2, y2)

if __name__ == "__main__":
    root = tk.Tk()
    app = RectangleApp(root)
    root.mainloop()