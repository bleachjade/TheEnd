def check_crash(player_x, player_y, bullet_x, bullet_y):
    if bullet_x - 52 < player_x < bullet_x + 52 and bullet_y - 23 < player_y < bullet_y + 23:
        return True
    else:
        return False