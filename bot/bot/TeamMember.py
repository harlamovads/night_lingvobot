from time import strftime
from keys import answer_dict, give_tips


class TeamMember:

    def __init__(self, name, score=0, solved=[], available_help=[]):
        self.available_help = available_help
        self.solved = solved
        self.name = name
        self.score = score

    def answer_check(self, task_idx, ans):
        if ans == answer_dict[task_idx]:
            if task_idx in self.solved:
                return 'Вы уже решили это задание! Попробуйте решить другие (они тоже интересные)'
            elif task_idx not in self.solved:
                self.score += 3
                self.solved.append(task_idx)
                with open('logging.txt', 'a') as log:
                    log.write(f'Команда {self.name} успешно решила задание {task_idx} в {strftime("%d %b %H:%M:%S")}\n')
                return 'Решение верное! Вы поймали три гласных, так держать'
        else:
            with open('logging.txt', 'a') as log:
                log.write(f'Команда {self.name} попыталась решить задание {task_idx} в {strftime("%d, %b, %H:%M:%S")}\n')
            return 'Пока неверно! Гласные улизнули, попробуйте ещё раз или возьмите подсказку'

    def get_some_help(self, task_idx):
        if task_idx in self.available_help:
            return give_tips[task_idx]
        elif 2 <= self.score and task_idx not in self.available_help:
            self.available_help.append(task_idx)
            self.score -= 2
            with open('logging.txt', 'a') as log:
                log.write(f'Команда {self.name} получила подсказку к заданию {task_idx} в {strftime("%d, %b, %H:%M:%S")}\n')
            return give_tips[task_idx]
        else:
            return 'У вас не хватает гласных, чтобы взять подсказку(\n Попробуйте еще раз или попробуйте решить другие задачи!'

    def point_getter(self):
        return self.score


if __name__ == "__main__":
    log = open('logging.txt', 'a')
    player = TeamMember('Stacy')
    message = input()
    task = message.split()[0]
    answer = message.split()[1]
    print(player.answer_check(task, answer))
    print(player.point_getter())
    task = input()
    print(player.get_some_help(task))
    print(player.point_getter())
    message = input()
    task = message.split()[0]
    answer = message.split()[1]
    print(player.answer_check(task, answer))
    print(player.point_getter())
