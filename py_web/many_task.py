import threading
import queue
import time

# 创建任务队列
order_queue = queue.Queue()
inventory_queue = queue.Queue()
email_queue = queue.Queue()


def handle_orders():
    while True:
        order = order_queue.get()
        print(f"Processing order {order}")
        time.sleep(1)  # 模拟处理订单的时间
        inventory_queue.put(order)
        order_queue.task_done()


def update_inventory():
    while True:
        order = inventory_queue.get()
        print(f"Updating inventory for order {order}")
        time.sleep(1)  # 模拟更新库存的时间
        email_queue.put(order)
        inventory_queue.task_done()


def send_emails():
    while True:
        order = email_queue.get()
        print(f"Sending email for order {order}")
        time.sleep(1)  # 模拟发送邮件的时间
        email_queue.task_done()


# 创建并启动线程
threading.Thread(target=handle_orders, daemon=True).start()
threading.Thread(target=update_inventory, daemon=True).start()
threading.Thread(target=send_emails, daemon=True).start()

# 添加一些订单到队列
for i in range(10):
    order_queue.put(i)

# 等待所有任务完成
order_queue.join()
inventory_queue.join()
email_queue.join()
