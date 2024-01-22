from time import strftime
from keys import answer_dict, task_grading, help_worth, give_tips


class TeamMember:

    def __init__(self, name):
        self.available_help = []
        self.solved = []
        self.name = name
        self.score = 0
        with open('logging.txt', 'a') as log:
            log.write(f'Команда {self.name} зарегистрировалась в {strftime("%d, %b, %H:%M:%S")}\n')

    def answer_check(self, task_idx, ans):
        if ans == answer_dict[task_idx]:
            if task_idx in self.solved:
                return 'Sorry, you have already solved this task'
            elif task_idx not in self.solved:
                if task_idx not in self.available_help:
                    self.score += task_grading[task_idx]
                elif task_idx in self.available_help:
                    self.score += task_grading[task_idx] - 1
                self.solved.append(task_idx)
                with open('logging.txt', 'a') as log:
                    log.write(f'Команда {self.name} успешно решила задание {task_idx} в {strftime("%d %b %H:%M:%S")}\n')
                return 'Good job!'
        else:
            with open('logging.txt', 'a') as log:
                log.write(f'Команда {self.name} попыталась решить задание {task_idx} в {strftime("%d, %b, %H:%M:%S")}\n')
            return 'Try again!'

    def get_some_help(self, task_idx):
        if task_idx in self.available_help:
            return give_tips[task_idx]
        elif help_worth[task_idx] <= self.score and task_idx not in self.available_help:
            self.available_help.append(task_idx)
            self.score -= help_worth[task_idx]
            with open('logging.txt', 'a') as log:
                log.write(f'Команда {self.name} получила подсказку к заданию {task_idx} в {strftime("%d, %b, %H:%M:%S")}\n')
            return give_tips[task_idx]
        else:
            return 'Sorry, you do not have enough points'

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
