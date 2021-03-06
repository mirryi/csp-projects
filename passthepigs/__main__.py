import os
from typing import Dict, List

import pygame
from pygame import Surface
from pygame.time import Clock

from simulation import (Pig, Player, PlayerState, Simulation, SimulationState,
                        Simulator, TossData, TossResult)
from simulation.ai import RandomPlayer, ThresholdPlayer


class PassThePigs:
    def __init__(self, players: List[Player], p1: Pig, p2: Pig):
        self._simulator = Simulator(players, p1, p2)

    def play(self):
        simulation = self._simulator.simulate()
        simgen = simulation.run()

        with Display() as display:
            playing = True
            stopped = False
            while not stopped:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        stopped = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            stopped = True

                if playing:
                    state = next(simgen)
                    display.update(state)


class Display:
    def __enter__(self):
        class DisplayInner:
            WIDTH = 600
            HEIGHT = 600

            TOP_MARGIN_TOP = 30
            TOP_MARGIN_LEFT = 30
            TOP_HEIGHT = 80

            def __init__(self):
                pygame.display.set_caption('Pass the Pigs')
                self._screen = pygame.display.set_mode(
                    [self.WIDTH, self.HEIGHT])
                self._clock = Clock()

                self._sprite_loader = PigSpriteLoader('sprites')

                self._score_font = pygame.font.SysFont(None, 48)
                self._name_font = pygame.font.SysFont(None, 24)

            def update(self, state: SimulationState):
                self.__draw_background()
                self.__draw_top(state.current_player, state.player_states)
                self.__draw_pigs(state.toss)
                self.__draw_bottom()

                pygame.display.flip()
                self._clock.tick(30)

            def __draw_background(self):
                self._screen.fill('white')

            def __draw_top(self, current_player: int,
                           players: List[PlayerState]):
                top_width = self.WIDTH - 2 * self.TOP_MARGIN_LEFT
                top_height = 100
                rect = (self.TOP_MARGIN_LEFT, self.TOP_MARGIN_TOP,
                        top_width, top_height)
                pygame.draw.rect(self._screen, 'gray', rect)

                box_width = top_width / len(players)
                box_height = top_height - 10
                for i, ps in enumerate(players):
                    box_left = int(self.TOP_MARGIN_LEFT + i * box_width)
                    box_top = self.TOP_MARGIN_TOP + 5
                    rect = (box_left, box_top,
                            box_width, box_height)

                    if i == current_player:
                        box_color = 'lightblue'
                    else:
                        box_color = 'lightgrey'
                    pygame.draw.rect(self._screen, box_color, rect)

                    score_text = self._score_font.render(
                        str(ps.score), True, 'black')
                    score_text_rect = score_text.get_rect()
                    score_text_height = score_text_rect.h
                    score_text_left = box_left + 10
                    score_text_top = int(
                        box_top + box_height / 2 - score_text_height / 2)
                    self.__blit(score_text, score_text_left, score_text_top)

                    name_text = self._name_font.render(
                        ps.player.name(), True, 'black')
                    self.__blit(name_text, score_text_left, box_top + 8)

            def __draw_pigs(self, toss: TossData):
                t1 = toss.t1
                t2 = toss.t2

                s1 = self._sprite_loader.load_sprite(t1)
                s2 = self._sprite_loader.load_sprite(t2)

                third_width = int(self.WIDTH / 3)
                half_height = int(self.HEIGHT / 2)
                s1_rect = s1.get_rect()
                s2_rect = s2.get_rect()

                self.__blit(s1, third_width - int(s1_rect.w / 2),
                            half_height - int(s1_rect.h / 2))
                self.__blit(s2, 2 * third_width - int(s2.get_rect().w / 2),
                            half_height - int(s2_rect.h / 2))

            def __draw_bottom(self):
                pass

            def __blit(self, image: Surface, left: int, top: int):
                rect = image.get_rect()
                rect.top = top
                rect.left = left
                self._screen.blit(image, rect)

        pygame.init()
        return DisplayInner()

    def __exit__(self, exc_type, exc_value, traceback):
        pygame.quit()


class PigSpriteLoader:
    _MAP = {
        TossResult.SIDE_DOT: 'side_dot',
        TossResult.SIDE_NO_DOT: 'side_no_dot',
        TossResult.RAZORBACK: 'razorback',
        TossResult.TROTTER: 'trotter',
        TossResult.SNOUTER: 'snouter',
        TossResult.LEANING_JOWLER: 'leaning_jowler',
    }

    def __init__(self, sprite_dir: str):
        self._sprite_dir = sprite_dir

        self._cache: Dict[TossResult, Surface] = {}

    def load_sprite(self, t: TossResult) -> Surface:
        if t in self._cache.keys():
            return self._cache[t]

        name = self.get_sprite_name(t)
        path = self.resolve_image_path(name)

        sprite = pygame.image.load(path)
        sprite.convert()

        self._cache[t] = sprite
        return sprite

    def get_sprite_name(self, t: TossResult) -> str:
        return self._MAP[t]

    def resolve_image_path(self, name: str) -> str:
        return os.path.join(self._sprite_dir, '{}.png'.format(name))


def main():
    rai = RandomPlayer(0.15)
    thai = ThresholdPlayer(5)

    p1 = Pig.standard()
    p2 = Pig.standard()

    game = PassThePigs([rai, thai], p1, p2)
    game.play()


if __name__ == '__main__':
    main()
