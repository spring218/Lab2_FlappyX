import os
import neat
import pickle
from flappy_game import Game, GameConfig

def eval_genomes(genomes, config):
    # Create game instance
    config = GameConfig()
    game = Game(config)
    
    # Create neural networks for each genome
    nets = []
    birds = []
    ge = []
    
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(game.bird)
        ge.append(genome)
    
    score = 0
    clock = pygame.time.Clock()
    
    while len(birds) > 0:
        clock.tick(30)
        
        # Get the next pipe
        pipe_ind = 0
        if len(game.pipes) > 1 and birds[0].x > game.pipes[0].x + game.pipes[0].width:
            pipe_ind = 1
        
        for x, bird in enumerate(birds):
            # Give each bird a fitness for staying alive
            ge[x].fitness += 0.1
            
            # Get input for neural network
            output = nets[x].activate((
                bird.y,
                abs(bird.y - game.pipes[pipe_ind].gap_y),
                abs(bird.y - (game.pipes[pipe_ind].gap_y + game.config.PIPE_GAP))
            ))
            
            # Make the bird jump if output > 0.5
            if output[0] > 0.5:
                bird.flap()
        
        # Update game state
        game.update()
        
        # Check for collisions
        for x, bird in enumerate(birds):
            if game.game_over:
                ge[x].fitness -= 1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        
        # Add score for passing pipes
        if game.score > score:
            score = game.score
            for g in ge:
                g.fitness += 5

def run(config_path):
    # Load configuration
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                              neat.DefaultSpeciesSet, neat.DefaultStagnation,
                              config_path)
    
    # Create population
    p = neat.Population(config)
    
    # Add reporters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    # Run for 50 generations
    winner = p.run(eval_genomes, 50)
    
    # Save the winner
    with open('winner.pkl', 'wb') as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path) 