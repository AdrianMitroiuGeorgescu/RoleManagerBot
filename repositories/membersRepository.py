import datetime

from main.db.db import Db


class MembersRepository(Db):
    def get_member(self, member_id):
        query = 'SELECT * FROM members m WHERE m.member_id = %s'
        result = self.record(query, member_id)
        return result

    def add_member(self, member_id):
        query = 'INSERT INTO members (member_id) VALUES ("%s")'
        self.execute(query, member_id)

    def remove_member(self, member_id):
        query = 'DELETE FROM members WHERE member_id = %s'
        self.execute(query, member_id)

    def save(self, member_dto):
        query = 'UPDATE members ' \
                'SET xp=%s, level_id=%s,' \
                'first_to_voice_channel=%s, modified=NOW(3),' \
                'joined_voice =%s, left_voice=%s,' \
                'time_spent = %s, steal_flag = %s,' \
                'messages_xp = %s, emojis_xp = %s,' \
                'web_xp = %s, share_xp = %s,' \
                'total_xp = %s ' \
                'WHERE member_id = %s'
        self.execute(query,
                     member_dto.xp,
                     member_dto.level_id,
                     member_dto.first_to_voice_channel,
                     member_dto.joined_voice,
                     member_dto.left_voice,
                     member_dto.time_spent,
                     member_dto.steal_flag,
                     member_dto.messages_xp,
                     member_dto.emojis_xp,
                     member_dto.web_xp,
                     member_dto.share_xp,
                     member_dto.xp + member_dto.messages_xp + member_dto.emojis_xp + member_dto.web_xp + member_dto.share_xp,
                     int(member_dto.member_id))

    def get_member_by_filters(self, filters):
        query  = 'SELECT * FROM members m WHERE '
        values = ()

        for item in filters:
            query = query + f'm.{item[0]} = %s '
            values = values + (item[1],)
            if item != filters[-1]:
                query = query + 'and '

        result = self.record(query, list(values)[0])
        return result

    def get_leaderboard(self):
        query  = 'SELECT * FROM members m WHERE total_xp > %s order by total_xp desc'
        results = self.records(query, 0)
        return results

    def get_leader(self):
        query  = 'SELECT * FROM members m WHERE total_xp > %s order by total_xp desc limit 1'
        result = self.record(query, 0)
        return result

    def get_participants_without_leader(self, member_dto):
        query   = 'SELECT * FROM members m WHERE m.total_xp > 0 AND m.member_id NOT IN (%s)'
        results = self.records(query, member_dto.member_id)
        return results

    def get_thief(self):
        query  = 'SELECT * FROM members m WHERE m.steal_flag = %s limit 1'
        result = self.record(query, 1)
        return result

    def reset_heist(self):
        query  = 'UPDATE members SET steal_flag = %s WHERE steal_flag = %s'
        self.execute(query, 0 , 1)

    def get_inactive_members(self):
        query   = 'SELECT * FROM members m WHERE m.modified < %s'
        results = self.records(query, datetime.datetime.now() - datetime.timedelta(30))
        return results
