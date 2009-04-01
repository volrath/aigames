from projectiles import *

class Weapon(object):
    def __init__(self):
        self.hit_state = 1
        self.shooting_force = 25

    def _dynamic_size(self):
        return self.hit_size
    size = property(_dynamic_size)

    def hit(self, increase_size):
        if self.original_size <= self.hit_size <= self.original_size * increase_size:
            self.hit_size += self.hit_state * .4
        else:
            if self.hit_size > self.original_size * increase_size:
                self.hit_size = self.original_size * increase_size
                self.hit_state = -1
                return True
            if self.original_size > self.hit_size:
                self.hit_size = self.original_size
                self.hit_state = 1
                return False
        return True


class SlashWeapon(Weapon):
    shooting_force = 20
    orientation = 5
    max_shooting_force = 50
    bullet_class = SlashNormalBullet
    color = 1., 234/255., 0.
    original_size = 3.2
    hit_size = 3.2

class SlashSuperWeapon(Weapon):
    shooting_force = 440
    orientation = 2
    max_shooting_force = 440
    bullet_class = SlashSuperBullet
    color = 1., 234/255., 0.
    original_size = 3.8
    hit_size = 3.8

class EnemyNormalWeapon(Weapon):
    shooting_force = 40
    orientation = 10
    max_shooting_force = 40
    bullet_class = EnemyBullet
    color = 84/255., 212/255., 244/255.
    original_size = 3.2
    hit_size = 3.2
