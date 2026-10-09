import tkinter as tk
import random

# Окно
root = tk.Tk()
root.title("Фермерский сбор")

WIDTH = 400
HEIGHT = 400

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT
)
canvas.pack()

# Фон
try:
    bg_image = tk.PhotoImage(file="img/tree.png")
    bg_id = canvas.create_image(
        0,
        0,
        image=bg_image,
        anchor="nw"
    )
except tk.TclError:
    print("Файл фона не найден — игра запустится без картинки.")
    bg_image = None

# Счёт и жизни
score = 0
lives = 3
game_active = True

score_text = canvas.create_text(
    50,
    20,
    text="Счёт: 0",
    font=("Arial", 14)
)

lives_text = canvas.create_text(
    330,
    20,
    text="❤️❤️❤️",
    font=("Arial", 14),
    fill="red"
)

# Корзинка
basket_x = 200
basket_y = 350

basket = canvas.create_text(
    basket_x,
    basket_y,
    text="🧺",
    font=("Arial", 35),
    fill="brown"
)

# Падающие предметы
objects = []

# Параметры сложности
base_speed = 4       # начальная скорость падения (пикселей за кадр)
base_delay = 60      # начальная задержка между кадрами (мс)
speed_per_10_points = 1   # на сколько ускоряется за каждые 10 очков
delay_per_10_points = 5    # на сколько уменьшается задержка за каждые 10 очков
max_speed = 12       # максимальная скорость
min_delay = 20       # минимальная задержка (чтобы игра не шла слишком быстро)

def get_current_speed():
    """Вычисляет текущую скорость падения на основе счёта"""
    extra_speed = (score // 10) * speed_per_10_points
    return min(base_speed + extra_speed, max_speed)

def get_current_delay():
    """Вычисляет текущий интервал обновления на основе счёта"""
    reduction = (score // 10) * delay_per_10_points
    return max(base_delay - reduction, min_delay)

# Создание предмета
def create_object():
    if not game_active:
        return

    x = random.randint(30, 370)
    y = 50

    # Распределение шансов: яблоко 60%, груша 20%, мусор 15%, бомба 5%
    rand = random.random()

    if rand < 0.05:  # 5% — бомба
        item = canvas.create_text(
            x,
            y,
            text="💣",
            font=("Arial", 25),
            fill="orange"
        )
        object_type = "bomb"

    elif rand < 0.20:  # 15% — мусор
        item = canvas.create_text(
            x,
            y,
            text="🥫",
            font=("Arial", 25),
            fill="red"
        )
        object_type = "trash"

    elif rand < 0.40:  # 20% — груша
        item = canvas.create_text(
            x,
            y,
            text="🍐",
            font=("Arial", 25),
            fill="green"
        )
        object_type = "pear"

    else:  # Оставшиеся 60% — яблоко
        item = canvas.create_text(
            x,
            y,
            text="🍎",
            font=("Arial", 25),
            fill="red"
        )
        object_type = "apple"

    objects.append([item, x, y, object_type])

    root.after(1000, create_object)


# Движение корзинки
def move_left(event):
    global basket_x

    if game_active and basket_x > 30:
        basket_x -= 20
        canvas.move(basket, -20, 0)


def move_right(event):
    global basket_x

    if game_active and basket_x < 370:
        basket_x += 20
        canvas.move(basket, 20, 0)


# Потеря жизни
def lose_life():
    global lives, game_active

    lives -= 1

    canvas.itemconfig(
        lives_text,
        text="❤️" * lives
    )

    if lives <= 0:
        game_active = False
        end_game()


# Игровой цикл
def update_game():
    global score

    if not game_active:
        return

    # Получаем текущие параметры сложности
    current_speed = get_current_speed()
    current_delay = get_current_delay()

    for obj in objects[:]:
        item = obj[0]
        x = obj[1]
        y = obj[2]
        object_type = obj[3]

        # Двигаем предмет вниз с текущей скоростью
        y += current_speed
        obj[2] = y

        canvas.move(item, 0, current_speed)

        # Проверка попадания в корзинку (зона ловли)
        if y >= 330 and y <= 370:
            if abs(x - basket_x) < 40:
                # Игрок поймал предмет
                if object_type == "apple":
                    score += 1
                    canvas.itemconfig(score_text, text=f"Счёт: {score}")

                elif object_type == "pear":
                    score += 2
                    canvas.itemconfig(score_text, text=f"Счёт: {score}")

                elif object_type == "trash":
                    lose_life()

                elif object_type == "bomb":
                    # Бомба отнимает 2 очка и 1 жизнь
                    score -= 2
                    canvas.itemconfig(score_text, text=f"Счёт: {score}")
                    lose_life()

                canvas.delete(item)
                objects.remove(obj)
                continue

        # Если предмет упал мимо (достиг низа экрана)
        if y > HEIGHT:
            if object_type == "apple" or object_type == "pear":
                # Яблоко и груша отнимают жизнь, если упали мимо
                lose_life()
            # Мусор и бомба при падении мимо ничего не делают

            canvas.delete(item)
            objects.remove(obj)

    # Обновляем с текущей задержкой
    if game_active:
        root.after(current_delay, update_game)


# Конец игры
def end_game():
    canvas.delete("all")

    canvas.create_text(
        WIDTH // 2,
        HEIGHT // 2 - 30,
        text="УРОЖАЙ СОБРАН!",
        font=("Arial", 24, "bold")
    )

    canvas.create_text(
        WIDTH // 2,
        HEIGHT // 2 + 20,
        text=f"Ты набрал {score} очков",
        font=("Arial", 16)
    )


# Управление
root.bind("<Left>", move_left)
root.bind("<Right>", move_right)

# Запуск игры
create_object()
update_game()

root.mainloop()
