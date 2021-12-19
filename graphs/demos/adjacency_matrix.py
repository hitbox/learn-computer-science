import argparse
import contextlib
import math
import os
import random
import textwrap

with contextlib.redirect_stdout(open(os.devnull,'w')):
    import pygame

from ..adjacency_matrix import AdjacencyMatrix

def is_colorful(name):
    return ('gray' not in name and 'grey' not in name and not name[-1].isdigit())

colorful = [color for key, color in pygame.color.THECOLORS.items() if is_colorful(key)]

random_spread = [x for x in range(-5, 6) if x != 0]

class Animation:

    def __init__(self, duration, elapsed=0):
        self.duration = duration
        self.elapsed = elapsed


def make_vertex_sprite(font, label, sprites_by_label, *groups):
    sprite = pygame.sprite.Sprite(*groups)
    sprite.label = label
    text = f'{sprite.label}'
    size = font.size(text)
    sprite.radius = max(size)
    sprite.color = (10,)*3
    sprite.radius_border = sprite.radius * 4
    text_image = font.render(text, True, sprite.color)
    size = (int(sprite.radius*2),)*2
    sprite.image = pygame.Surface(size, flags=pygame.SRCALPHA)
    rect = sprite.image.get_rect()
    #
    pygame.draw.circle(sprite.image, (200,)*3, rect.center, sprite.radius)
    pygame.draw.circle(sprite.image, sprite.color, rect.center, sprite.radius, 1)
    sprite.image.blit(text_image, text_image.get_rect(center=rect.center))
    #
    sprite.rect = sprite.image.get_rect()
    sprite.center = pygame.Vector2(sprite.rect.center)
    return sprite

def edge_or_vertex(s):
    if '-' in s:
        v1, v2 = map(str.strip, s.split('-'))
        return v1, v2
    else:
        return tuple(s.strip())

def make_graph_args(graph_strings):
    # keep actual edges
    edges = [edge_or_vertex
             for edge_or_vertex in graph_strings
             if len(edge_or_vertex) > 1]
    # flatten edges list into unique vertices
    vertices = set(v for edge in edges for v in edge)
    return (vertices, edges)

def loop(graph, commands):
    framerate = 60

    command_animation = Animation(duration=framerate * .5)
    command = None
    history = []
    last_vertices = graph.vertices.copy()

    pygame.font.init()
    screen = pygame.display.set_mode((800, 700))
    background = screen.copy()
    frame = screen.get_rect()
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()
    group = pygame.sprite.Group()
    sprites_by_label = {}

    dragging = None
    hovering = None
    running = True
    while running:
        # tick
        elapsed = clock.tick(framerate)
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dragging.rect.move_ip(event.rel)
                    dragging.center.x = dragging.rect.centerx
                    dragging.center.y = dragging.rect.centery
                else:
                    for sprite in group:
                        dist = math.dist(sprite.rect.center, event.pos)
                        if dist <= sprite.radius:
                            hovering = sprite
                            break
                    else:
                        hovering = None
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for sprite in group:
                    if sprite.rect.collidepoint(event.pos):
                        dragging = sprite
                        break
                else:
                    dragging = None
        # update
        if commands:
            command_animation.elapsed += 1
            if command_animation.elapsed == command_animation.duration:
                if command is not None:
                    history.append(command)
                command = commands.pop(0)
                command_animation.elapsed = 0
        else:
            # once commands is exhausted adjust radius border
            for sprite in group:
                sprite.radius_border = sprite.radius * 2

        # execute commands
        if command is not None:
            f, *args = command
            f(*args)
        # examine changes to vertices
        if last_vertices != graph.vertices:
            change = set(graph.vertices).difference(last_vertices)
            for label in change:
                sprite = make_vertex_sprite(font, label, sprites_by_label, group)
                sprites_by_label[label] = sprite
                cx, cy = frame.center
                cx += random.choice(random_spread)
                cy += random.choice(random_spread)
                sprite.rect.center = (cx, cy)
                sprite.center = pygame.Vector2(sprite.rect.center)
            last_vertices = graph.vertices.copy()
        # update - detect collisions
        collisions = []
        _sprites = group.sprites()
        for sprite1 in _sprites:
            for sprite2 in _sprites:
                if sprite1 is sprite2:
                    continue
                dist = math.dist(sprite1.center, sprite2.center)
                if dist == 0 or dist <= (sprite1.radius_border + sprite2.radius_border):
                    collisions.append((sprite1, sprite2))
        # update - resolve collisions
        for sprite1, sprite2 in collisions:
            dy = sprite2.center.y - sprite1.center.y
            dx = sprite2.center.x - sprite1.center.x
            angle = math.atan2(dy, dx)
            dist = math.dist(sprite1.center, sprite2.center)
            radii = (sprite1.radius_border + sprite2.radius_border)
            move_step = (radii - dist) * 0.10
            sprite1.center.x -= math.cos(angle) * move_step
            sprite1.center.y -= math.sin(angle) * move_step
            sprite2.center.x += math.cos(angle) * move_step
            sprite2.center.y += math.sin(angle) * move_step

            sprite1.rect.center = sprite1.center
            sprite2.rect.center = sprite2.center
        # draw
        screen.blit(background, (0,0))

        # TODO: draw history of commands like scrollback like command line.

        # draw - matrix table
        table = [[None]*graph.nvertices for _ in range(graph.nvertices)]
        for ri, row in enumerate(graph.adjacency_matrix):
            for ci, col in enumerate(row):
                vertex1 = graph.vertices_list[ri]
                vertex2 = graph.vertices_list[ci]
                if col == AdjacencyMatrix.notset:
                    text_image = None
                else:
                    text_image = small_font.render(f'{vertex1}-{vertex2}', True, (200,)*3)
                table[ri][ci] = text_image

        cell_width = 0
        cell_height = 0
        for row in table:
            _width = max((image.get_width() for image in row if image is not None), default=0)
            if _width > cell_width:
                cell_width = _width
            _height = max((image.get_height() for image in row if image is not None), default=0)
            if _height > cell_height:
                cell_height = _height
        cell_width *= 1.5
        cell_height *= 1.5

        table_image = pygame.Surface((cell_width*graph.nvertices, cell_height*graph.nvertices))
        empty = pygame.Surface((cell_width, cell_height))

        for ri, row in enumerate(table):
            for ci, image in enumerate(row):
                if image is None:
                    image = empty
                table_image.blit(image,(ri*cell_width, ci*cell_height))

        rect = table_image.get_rect(center=frame.center)
        screen.blit(table_image, rect)
        pygame.draw.rect(screen, (200,)*3, rect.inflate(4,4), 1)

        # draw - edges
        for label1, label2, _ in graph.get_edges():
            sprite1 = sprites_by_label[label1]
            sprite2 = sprites_by_label[label2]
            pygame.draw.line(screen, (200,)*3, sprite1.rect.center, sprite2.rect.center)

        # draw - sprites
        group.draw(screen)
        # draw - hovering cursor
        if hovering:
            pygame.draw.circle(screen, (200,30,30), hovering.rect.center, hovering.radius*1.5, 1)

        pygame.display.flip()


def main(argv=None):
    """
    Demonstrate adjacency matrix graph representation.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('graph', nargs='+', type=edge_or_vertex)
    args = parser.parse_args(argv)

    # create commands to build the graph in an animated fashion
    vertices, edges = make_graph_args(args.graph)

    graph = AdjacencyMatrix(len(vertices))

    commands = []
    for index, vertex in enumerate(sorted(vertices)):
        commands.append((graph.set_vertex, index, vertex))
    for edge in edges:
        v1, v2 = edge
        commands.append((graph.set_edge, v1, v2))

    loop(graph, commands)

if __name__ == '__main__':
    main()
