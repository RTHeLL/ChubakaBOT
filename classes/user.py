class User:
    def __init__(self, vk, sql):
        self.sql = sql
        self.vk = vk

    def get(self, user_id):
        try:
            data = self.sql.fetchOne('SELECT * FROM users WHERE user_id = %d' % user_id)
            return data
        except:
            return False

    def create(self, user_id):
        user = self.vk.method('users.get', {'user_id': user_id})

        print('Новый участник: %s %s' % (user['response'][0]['first_name'], user['response'][0]['last_name']))

        self.sql.ex('INSERT INTO `users` (`user_id`, `user_name`, `join`) VALUES (\'%d\', \'%s %s\', \'1\')' % (
            user_id, user['response'][0]['first_name'], user['response'][0]['last_name']))

        return self.sql.fetchOne('SELECT * FROM users WHERE user_id = %d' % user_id)

    def me(self, user_id, user):

        if user[5] == 0:
            num = 0
        else:
            num = (user[4] / user[5]) * 100

        if user[13] == 0:
            self.vk.sendMessage(user_id,
                                'Правильно выполнено: %d\nВсего выполнено: %d\nПравильность выполнения: *id0('
                                '%.1f%%)\n\nСтатус: *id0(%s)' % (
                                    user[4], user[5], num, self.get_level(user[4])))
        else:
            self.vk.sendMessage(user_id,
                                'Правильно выполнено: %d\nВсего выполнено: %d\nПравильность выполнения: *id0('
                                '%.1f%%)\n\nСтатус: *id0(%s)\nАдминистратор *id0(%d) уровня.' % (
                                    user[4], user[5], num, self.get_level(user[4]), user[13]))

    def top(self, user_id):
        data = self.sql.fetchAll('SELECT user_id, user_name, tests FROM users ORDER BY tests DESC LIMIT 5')

        text = ''
        i = 1

        for user in data:
            text = text + '\n%d *id%d(%s) - \tВерные ответы: %d' % (i, user[0], user[1], user[2])
            i += 1

        self.vk.sendMessage(user_id, text)

    @staticmethod
    def get_level(post):
        return {
            post == 0: 'Новичек',
            1 <= post <= 4: 'Ученик',
            5 <= post <= 9: 'Студент',
            10 <= post <= 19: 'Профи',
            20 <= post <= 49: 'Магистр',
            50 <= post <= 99: 'Гуру',
            100 <= post <= 249: 'Мудрец',
            250 <= post <= 499: 'Оракул',
            500 <= post <= 999: 'Гений',
            post >= 1000: 'ВЫСШИЙ РАЗУМ'
        }[True]
