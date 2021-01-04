# coding: utf-8

class Tasks:
    def __init__(self, vk, sql):
        self.vk = vk
        self.sql = sql

    def show(self, user_id, task_id, mode):
        task = self.sql.fetchOne('SELECT * FROM rus WHERE id = %d' % task_id)
        text = ''

        if mode == 2 and task_id == 81:
            text += 'Вы начали режим РТ!\nЧто бы выйти, напишите "стоп".\n\n'

        text += '*id0(%s) (%d). %s\n\n' % (task[1], task[0], task[2])

        n = 3

        if task[4]:
            for i in range(5):
                if n == 7:
                    text += '%d) %s.\n' % (i + 1, task[n])
                else:
                    text += '%d) %s;\n' % (i + 1, task[n])
                n += 1
        else:
            text += '%s.\n' % task[3]

        if not mode == 5:
            text += '\nОтвет (цифры, через запятую):'
            self.sql.ex('UPDATE users SET `tmp_test` = \'%d\', `tmp_type` = \'%s\', `tmp_cor` = \'%s\', `mode` = '
                        '\'%d\' WHERE `user_id` = \'%d\';' % (task_id, task[1], task[8], mode, user_id))
        elif mode == 5:
            text += '\nОтвет: *id0(%s)' % task[8]

        self.vk.sendMessage(user_id, text)

    def get_correct(self, user_id, user, answer):

        true = ''
        false = ''
        score = 0

        if user[3] == answer:
            if user[8] == 0:
                self.vk.sendMessage(user_id, 'Верно!\nВведите РУС чтобы продолжить.')
                a_t = 'tests + 1'

            elif user[8] == 1:
                self.vk.sendMessage(user_id, 'Верно!')

            elif user[8] == 2:
                true = user[6] + ', '
                score = 4

        else:
            if user[8] == 0:
                string = 'Неверно!\nПравильный ответ: *id0(%s)\nВведите РУС чтобы продолжить.' % user[3]
                self.vk.sendMessage(user_id, string)
                a_t = 'tests'

            elif user[8] == 1:
                string = 'Неверно!\nПравильный ответ: *id0(%s)' % user[3]
                self.vk.sendMessage(user_id, string)

            elif user[8] == 2:
                false = user[6] + ', '

        if user[8] == 0:
            sql = 'UPDATE users SET tmp_test = 0, tmp_cor = 0, tmp_type = \'\', all_tests = all_tests+1, ' \
                  'mode = 0, tests = %s WHERE user_id = %d;' % (a_t, user_id)
        elif user[8] == 1:
            sql = 'UPDATE users SET tmp_test = 0, tmp_type = \'\', tmp_cor = 0, mode = 0 WHERE user_id ' \
                  '= %d;' % user_id
        elif user[8] == 2:
            sql = 'UPDATE users SET mode_true = CONCAT(`mode_true`, \'%s\'), mode_false = CONCAT(' \
                  '`mode_false`, \'%s\'), mode_score = mode_score + %d WHERE user_id = %d' % (true,
                                                                                              false,
                                                                                              score,
                                                                                              user_id)

        self.sql.ex(sql)

        if user[8] == 2 and user[2] < 107:
            self.show(user_id, user[2] + 1, 2)
        elif user[8] == 2 and user[2] == 107:
            info = self.sql.fetchOne('SELECT mode_true, mode_false, mode_score FROM users WHERE user_id = %d' % user_id)
            text = 'Ваш результат: *id0(%d баллов) из 100\n\n' % info[2]

            if len(info[0]) > 0:
                true = info[0]
                true = true[:-2]
                text += 'Верные ответы: %s.\n' % true

            if len(info[1]) > 0:
                false = info[1]
                false = false[:-2]
                text += 'Неверные ответы: %s.' % false

            self.sql.ex(
                'UPDATE users SET tmp_test = 0, tmp_type = \'\', tmp_cor = 0, mode = 0, mode_true = \'\', mode_false '
                '= \'\', mode_score = 0 WHERE user_id = %d;' % user_id)

            self.vk.sendMessage(user_id, text)

    def convert_ans(self, answer, user_id, user):
        arr = answer.replace(' ', '').split(',')
        if self.check_int(arr[0]):
            arr.sort()
            correct = ''

            for ans in arr:
                if self.check_int(ans): correct += ans + ','

            correct = correct[0:-1]

            self.get_correct(user_id, user, correct)
        else:
            return False

    def check_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False
