import pygame
import random

# inicializace hry
pygame.init()

# obrazovka
width = 1200
height = 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bitva s mozkomory")


# nastaveni hry
fps = 60
clock = pygame.time.Clock()


# Classy
class Game:
    def __init__(self, our_player, group_of_mozkomors):
        self.score = 0
        self.round_number = 0

        self.round_time = 0
        self.slow_down_cycle = 0

        self.our_player = our_player
        self.group_of_mozkomors = group_of_mozkomors

        # hudba v pozadi
        pygame.mixer.music.load("media/bg-music-hp.wav")
        pygame.mixer.music.play(-1, 0.0)

        # fonty
        self.potter_font = pygame.font.Font("fonts/Harry.ttf", 24)
        self.potter_font_big = pygame.font.Font("fonts/Harry.ttf", 45)

        # obrazek v pozadi
        self.background_image = pygame.image.load("../bitvaFlask/img/bg-dementors.png")
        self.background_image_rect = self.background_image.get_rect()
        self.background_image_rect.topleft = (0, 0)

        # obrazky
        blue_image = pygame.image.load("../bitvaFlask/img/mozkomor-modry.png")
        green_image = pygame.image.load("../bitvaFlask/img/mozkomor-zeleny.png")
        purple_image = pygame.image.load("../bitvaFlask/img/mozkomor-ruzovy.png")
        yellow_image = pygame.image.load("../bitvaFlask/img/mozkomor-zluty.png")
        # typy mozkomoru: 0 = modry, 1= zel, 2 = ruzo, 3 = zlut
        self.mozkomors_images = [blue_image, green_image, purple_image, yellow_image]

        # generujeme mozkomora, ktereho chceme chytit
        self.mozkomor_catch_type = random.randint(0, 3)
        self.mozkomor_catch_image = self.mozkomors_images[self.mozkomor_catch_type]

        self.mozkomor_catch_image_rect = self.mozkomor_catch_image.get_rect()
        self.mozkomor_catch_image_rect.centerx = width // 2
        self.mozkomor_catch_image_rect.top = 25

    # kod, ktery je volan stale dokola
    def update(self):
        self.slow_down_cycle += 1
        if self.slow_down_cycle == fps:
            self.round_time += 1
            self.slow_down_cycle = 0
            print(self.round_time)

        # kontrola kolize
        self.check_collisions()

    # vykresluje vse ve hre - texty, hledaneho mozkomora
    def draw(self):
        dark_yellow = pygame.Color("#BAA400")
        blue = (21, 31, 217)
        green = (24, 194, 38)
        purple = (195, 23, 189)
        yellow = (195, 181, 23)
        # typy mozkomoru: 0 = modry, 1= zel, 2 = ruzo, 3 = zlut
        colors = [blue, green, purple, yellow]

        # nastaveni textu
        catch_text = self.potter_font.render("Chyt tohoto mozkomora", True, dark_yellow)
        catch_text_rect = catch_text.get_rect()
        catch_text_rect.centerx = width // 2
        catch_text_rect.top = 5

        score_text = self.potter_font.render(f"Skore: {self.score}", True, dark_yellow)
        score_text_rect = score_text.get_rect()
        score_text_rect.topleft = (10, 4)

        lives_text = self.potter_font.render(f"Zivoty: {self.our_player.lives}", True, dark_yellow)
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.topleft = (10, 30)

        round_text = self.potter_font.render(f"Kolo: {self.round_number}", True, dark_yellow)
        round_text_rect = round_text.get_rect()
        round_text_rect.topleft = (10, 60)

        time_text = self.potter_font.render(f"Cas kola: {self.round_time}", True, dark_yellow)
        time_text_rect = time_text.get_rect()
        time_text_rect.topright = (width - 10, 5)

        # pocet, kolikrat se muze harry vratit do bezpecne zony
        back_safe_zone_text = self.potter_font.render(f"Bezpecna zona: {self.our_player.enter_safe_zone}", True, dark_yellow)
        back_safe_zone_text_rect = back_safe_zone_text.get_rect()
        back_safe_zone_text_rect.topright = (width - 10, 35)

        # vykresleni(blitting) do obrazovky
        screen.blit(catch_text, catch_text_rect)
        screen.blit(score_text, score_text_rect)
        screen.blit(lives_text, lives_text_rect)
        screen.blit(round_text, round_text_rect)
        screen.blit(time_text, time_text_rect)
        screen.blit(back_safe_zone_text, back_safe_zone_text_rect)

        # obrazek mozkomora, ktereho mame chytit
        screen.blit(self.mozkomor_catch_image, self.mozkomor_catch_image_rect)

        # tvary
        # ramecek herni plochu pro mozkomory - kde se mohou mozkomorove pohybovat
        pygame.draw.rect(screen, colors[self.mozkomor_catch_type], (0, 100, width, height - 200), 5)

    # kontroluje kolizi harryho s mozkomorem
    def check_collisions(self):
        # s jakym mozkomorem jsme se srazili?
        collided_mozkomor = pygame.sprite.spritecollideany(self.our_player, self.group_of_mozkomors)

        if collided_mozkomor:
            # srazili jsme se se spravnym mozkomorem?
            if collided_mozkomor.type == self.mozkomor_catch_type:
                # prehrajeme zvuk chyceni spravneho mozkomora
                self.our_player.catch_sound.play()
                # zvysime skore
                self.score += 10 * self.round_number
                # odstraneni chyceneho mozkomora
                collided_mozkomor.remove(self.group_of_mozkomors)
                # existuji dalsi mozkomorove, ktere muzeme chytat?
                if self.group_of_mozkomors:
                    self.choose_new_target()
                else:
                    # kolo je dokoncene - vsechnz mozkomory jsme chytili
                    self.our_player.reset()
                    self.start_new_round()
            else:
                self.our_player.wrong_sound.play()
                self.our_player.lives -= 1
                # je hra u konce? = dosly zivoty?
                if self.our_player.lives <= 0:
                    self.pause_game(f"Dosazene skore: {self.score}", "Stisknete Enter, pokud chcete hrat znova")
                    self.reset_game()
                self.our_player.reset()

    # zahaji nove kolo - s vetsim poctem mozkomoru v herni plose
    def start_new_round(self):
        # pri dokonceni kola poskytneme bonus podle toho, jak rychle hrac kolo dokonci: drive = vice bodu
        self.score += int(100 * (self.round_number / (1 + self.round_time)))

        # resetujeme hodnoty
        self.round_time = 0
        self.slow_down_cycle = 0
        self.round_number += 1
        self.our_player.enter_safe_zone += 1

        # vycistime skupinu mozkomoru, abychom mohli skupinu naplnit novymi mozkomory
        for deleted_mozkomor in self.group_of_mozkomors:
            self.group_of_mozkomors.remove(deleted_mozkomor)

        for _ in range(self.round_number):
            for i in range(4):
                self.group_of_mozkomors.add(Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164), self.mozkomors_images[i], i))

                # vybirame noveho mozkomora, ktereho mame chytit
                self.choose_new_target()

    # vybira noveho mozkomora, ktereho mame chytit
    def choose_new_target(self):
        new_mozkomor_to_catch = random.choice(self.group_of_mozkomors.sprites())
        self.mozkomor_catch_type = new_mozkomor_to_catch.type
        self.mozkomor_catch_image = new_mozkomor_to_catch.image

    # pozastaveni hry - pauza pred zahajenim nove hru, na zacatku pri spousteni
    def pause_game(self, main_text, subheading_text):
        # ↓tohle je prasarna ↓
        global lets_continue
        # ↑tohle je prasarna ↑ (vsak jedno pouziti "global" by projit snad mohlo)

        # nastavime barvy
        dark_yellow = pygame.Color("#BAA400")
        black = (0, 0, 0)

        # hlavni text pro pauznuti
        main_text_create = self.potter_font_big.render(main_text, True, dark_yellow)
        main_text_create_rect = main_text_create.get_rect()
        main_text_create_rect.center = (width // 2, height // 2 - 35)

        # podnadpis pro pauznuti
        subheading_text_create = self.potter_font_big.render(subheading_text, True, dark_yellow)
        subheading_text_create_rect = subheading_text_create.get_rect()
        subheading_text_create_rect.center = (width//2, height//2 + 35)

        # zobrazeni hlavniho textu a podnadpisu
        screen.fill(black)
        screen.blit(main_text_create, main_text_create_rect)
        screen.blit(subheading_text_create, subheading_text_create_rect)

        pygame.display.update()

        # zastaveni hry
        paused = True
        while paused:
            for one_event in pygame.event.get():
                if one_event.type == pygame.KEYDOWN:
                    if one_event.key == pygame.K_RETURN:
                        paused = False
                if one_event.type == pygame.QUIT:
                    paused = False
                    lets_continue = False

    # resetuje hru do vychoziho stavu
    def reset_game(self):
        self.score = 0
        self.round_number = 0

        self.our_player.lives = 5
        self.our_player.enter_safe_zone = 3
        self.start_new_round()

        # spusteni muziky v pozadi
        pygame.mixer.music.play(-1, 0.0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("../bitvaFlask/img/potter-icon.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = width//2
        self.rect.bottom = height - 8

        self.lives = 5
        self.enter_safe_zone = 3
        self.speed = 8

        self.catch_sound = pygame.mixer.Sound("media/expecto-patronum.mp3")
        self.catch_sound.set_volume(0.1)
        self.wrong_sound = pygame.mixer.Sound("media/wrong.wav")
        self.catch_sound.set_volume(0.1)

    # kod, ktery je volan stale dokola
    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < width:
            self.rect.x += self.speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 100:
            self.rect.y -= self.speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < (height-100):
            self.rect.y += self.speed

    # navrat do bezpecne zony dole v herni plose
    def back_to_safe_zone(self):
        if self.enter_safe_zone > 0:
            self.enter_safe_zone -= 1
            self.rect.bottom = height - 8

    # vraci hrace zpet na vychozi pozici - doprostred bezpecne zony
    def reset(self):
        self.rect.centerx = width//2
        self.rect.bottom = height - 8


class Mozkomor(pygame.sprite.Sprite):
    def __init__(self, x, y, image, mozkomor_type):
        super().__init__()
        # nahrajeme obrazek mozkomora a umistime ho
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # typy mozkomoru: 0 = modry, 1= zel, 2 = ruzo, 3 = zlut
        self.type = mozkomor_type

        # nastaveni nahodneho smeru mozkomora
        self.x = random.choice([-1, 1])
        self.y = random.choice([-1, 1])
        self.speed = random.randint(1, 5)

    # kod, ktery je volan stale dokola
    def update(self):
        # pohyb mozkomora
        self.rect.x += self.x * self.speed
        self.rect.y += self.y * self.speed

        # odraz mozkomora
        if self.rect.left < 0 or self.rect.right > width:
            self.x = -1 * self.x
        if self.rect.top < 100 or self.rect.bottom > (height - 100):
            self.y = -1 * self.y

# ================================================================================= #

# skupina mozkomoru
mozkomor_group = pygame.sprite.Group()
# testovaci mozkomorove
# typy mozkomoru: 0 = modry, 1= zel, 2 = ruzo, 3 = zlut
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-modry.png"), 0)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-zeleny.png"), 1)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-ruzovy.png"), 2)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-zluty.png"), 3)
# mozkomor_group.add(one_mozkomor)

# skupina hracu
player_group = pygame.sprite.Group()
one_player = Player()
player_group.add(one_player)

# objekt Game
my_game = Game(one_player, mozkomor_group)
my_game.start_new_round()

# hlavni cyklus hry
lets_continue = True
my_game.pause_game("Harry Potter a bitva s mozkomory", "Stiskni Enter pro zahajeni hry") # presunuto z pozice mezi my_game a my_game.start_new_round(pauznuta hra se nedala vypnout krizkem)
while lets_continue:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            lets_continue = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                one_player.back_to_safe_zone()

    # vyplneni plochy
    # screen.fill((0, 0, 0))
    screen.blit(my_game.background_image, my_game.background_image_rect)

    # updatujeme skupinu mozkomoru
    mozkomor_group.draw(screen)
    mozkomor_group.update()

    # udpatujeme skupinu hracu(jeden hrac)
    player_group.draw(screen)
    player_group.update()

    # updatujeme objekt vytvoreny podle classy Game
    my_game.update()
    my_game.draw()

    # update obrazovky
    pygame.display.update()

    # zpomaleni cykly
    clock.tick(fps)

# ukonceni hry
pygame.quit()
