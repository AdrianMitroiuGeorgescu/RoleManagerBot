from entities.members import MemberDto


def check_minimum_xp(member_id: int, xp: int):
    member_dto = MemberDto()
    member_dto.get_member(member_id)
    if member_dto.xp < xp:
        return False
    return True
