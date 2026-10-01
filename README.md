# Webots Autonomous & Evolutionary Robotics

A Webots robotics project developed during my university studies exploring two approaches to autonomous mobile-robot control: a manually designed **behaviour-based robotics (BBR) controller** and an **evolutionary neural-network controller** optimised using a genetic algorithm.

The behaviour-based controller combines ground, proximity and light-sensor information to perform line following, obstacle avoidance and beacon-based route selection. The evolutionary controller instead uses a multilayer perceptron (MLP) to map sensor observations to differential-drive motor commands, with the network weights evolved using a genetic algorithm.

Together, the implementations provide an interesting comparison between explicitly engineered robot behaviour and behaviour produced through evolutionary optimisation.

## Project Overview

The control architecture can be represented as:

```text
                 WEBOTS ROBOT
                      |
          +-----------+-----------+
          |                       |
          v                       v
   3 Ground Sensors        8 Proximity Sensors
          |                       |
          +-----------+-----------+
                      |
                      v
                11 MLP Inputs
                      |
                      v
              10 Hidden Neurons
                      |
                      v
                2 MLP Outputs
                      |
              +-------+-------+
              |               |
              v               v
          Left Motor      Right Motor
```

The neural-network weights are not manually tuned.

Instead, a Webots Supervisor evaluates candidate weight sets and uses a genetic algorithm to evolve new populations based on their measured fitness.

## Technologies

- Python
- Webots
- Evolutionary Robotics
- Genetic Algorithms
- Neural Networks
- Neuroevolution
- NumPy
- Autonomous Mobile Robotics

## Repository Structure

```text
webots-evolutionary-robotics/
│
├── README.md
├── LICENSE
│
└── controllers/
    ├── robot/
    │   ├── er-robot.py
    │   └── mlp.py
    │
    └── supervisor/
        ├── supervisor.py
        └── ga.py
```

## System Architecture

The project consists of two principal runtime components:

```text
            WEBOTS SUPERVISOR
                   |
                   | Candidate genotype
                   | Neural-network weights
                   v
             ROBOT CONTROLLER
                   |
                   | Sensor observations
                   v
            Neural Network
                   |
                   | Motor commands
                   v
                 Robot
                   |
                   | Behaviour
                   v
             Fitness Value
                   |
                   +-------------------->
                        Supervisor
```

The Supervisor manages the evolutionary process while the robot controller evaluates each candidate neural-network controller through interaction with the simulated environment.

## Behaviour-Based Controller

The repository also contains a manually designed behaviour-based robot controller.

Unlike the evolutionary controller, where motor behaviour emerges from neural-network weights optimised by the genetic algorithm, the BBR controller explicitly defines how the robot should respond to different sensor conditions.

The controller integrates:

- 3 ground sensors
- 8 proximity sensors
- 4 light sensors
- Differential-drive motors

The resulting sensor-processing architecture is:

```text
                  SENSOR INPUTS
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
 Ground Sensors   Proximity Sensors  Light Sensors
       │               │               │
       ▼               ▼               ▼
 Line Following   Obstacle Detection  Beacon Detection
       │               │               │
       └───────────────┼───────────────┘
                       ▼
                Behaviour Logic
                       │
                       ▼
               Left / Right Motor
                    Commands
```

### Line Following

The three ground sensors represent the left, centre and right regions beneath the robot.

The controller compares these readings to determine the required steering behaviour.

Conceptually:

```text
Left strongest     -> steer right
Centre strongest   -> move forward
Right strongest    -> steer left
```

This produces a simple reactive line-following controller using differential wheel speeds.

### Obstacle Detection and Avoidance

The eight proximity sensors monitor the environment surrounding the robot.

When the proximity measurements exceed the configured detection threshold, the controller identifies an obstacle and transitions from normal line-following behaviour into obstacle avoidance.

The controller then manoeuvres around the obstacle while monitoring the ground sensors for the line.

Once the line is detected again, normal navigation can resume.

```text
Follow Line
    │
    ▼
Obstacle Detected?
    │
   Yes
    │
    ▼
Avoid Obstacle
    │
    ▼
Search for Line
    │
    ▼
Line Reacquired
    │
    ▼
Resume Navigation
```

The controller also maintains an obstacle count so that previous interactions can influence subsequent route behaviour.

### Beacon-Based Route Selection

Four light sensors provide information used for beacon detection.

The beacon state influences which route the robot selects when reaching a fork in the course.

The controller maintains separate state flags representing Route A and Route B behaviour.

Conceptually:

```text
             Reach Fork
                 │
          Detect Beacon State
                 │
          ┌──────┴──────┐
          │             │
      Beacon On     Beacon Off
          │             │
          ▼             ▼
       Route A       Route B
```

This introduces environmental context into the navigation behaviour rather than relying solely on line-following information.

### Behaviour State

Several internal flags are used to maintain information about the robot's current behaviour, including:

- Whether an obstacle has been detected
- Whether the robot has returned to the line
- Whether an obstacle was previously encountered
- Number of obstacles cleared
- Beacon state
- Fork-turn state
- Route A / Route B selection

This allows the controller to combine reactive sensor responses with a limited amount of behavioural state.

## Behaviour-Based vs Evolutionary Control

Having both controllers provides a useful comparison between two approaches to autonomous robot behaviour.

```text
BEHAVIOUR-BASED CONTROL
          │
          ├── Human-designed rules
          ├── Explicit thresholds
          ├── Explicit behaviours
          ├── Predictable decisions
          └── Manual tuning


EVOLUTIONARY CONTROL
          │
          ├── Neural network
          ├── Sensor-to-motor mapping
          ├── Fitness function
          ├── Genetic algorithm
          └── Evolved parameters
```

The behaviour-based controller explicitly encodes how the robot should respond to particular sensor conditions.

The evolutionary controller instead defines an objective through its fitness function and allows the optimisation process to search for neural-network weights that produce useful behaviour.

Exploring both approaches provided practical experience with the trade-off between directly engineering autonomous behaviour and allowing control behaviour to emerge through optimisation.

## Neural Network

The robot controller uses a multilayer perceptron with the architecture:

```text
11 Inputs
    |
    v
10 Hidden Neurons
    |
    v
2 Outputs
```

The 11 input neurons consist of:

- 3 ground-sensor measurements
- 8 proximity-sensor measurements

The two output neurons determine:

- Left-wheel velocity
- Right-wheel velocity

Sensor values are normalised before being supplied to the neural network.

The network output is then converted into differential-drive motor commands.

## Ground Sensors

Three downward-facing ground sensors provide information about the surface beneath the robot:

```text
Left
Centre
Right
```

Their values are normalised between 0 and 1 before being passed to the neural-network controller.

These inputs provide the sensory information required for line-following behaviour.

## Proximity Sensors

Eight proximity sensors provide information about surrounding obstacles.

Each sensor reading is normalised before being added to the neural-network input vector.

The resulting controller therefore receives information about both:

```text
Environment below robot
        +
Environment around robot
        |
        v
Neural Controller
```

## Fitness Function

A key part of evolutionary robotics is defining a fitness function that rewards desirable behaviour.

The implementation combines several behavioural objectives.

### Forward Motion

The average wheel velocity is used to reward forward movement.

Conceptually:

```text
Left Velocity + Right Velocity
------------------------------
              2
```

Higher forward velocity therefore contributes positively to fitness.

### Suppressing Spinning

The difference between the two wheel velocities is measured to discourage behaviour in which the robot simply rotates rather than progressing through the environment.

```text
| Left Velocity - Right Velocity |
```

Large differences between wheel speeds therefore reduce the quality of the behaviour.

### Obstacle Avoidance

Readings from the eight proximity sensors are combined and normalised.

Higher obstacle proximity contributes a penalty to the resulting fitness calculation, encouraging controllers that avoid collisions.

### Line Following

The three ground-sensor inputs are combined to provide a line-following component.

The complete fitness function therefore attempts to evolve behaviour balancing:

```text
                 FITNESS
                    |
       +------------+------------+
       |            |            |
       v            v            v
    Forward       Avoid       Follow
     Motion      Spinning      Line
                    |
                    v
             Avoid Obstacles
```

Rather than optimising only speed, the controller must balance several behavioural requirements.

## Genetic Algorithm

The Webots Supervisor manages the genetic algorithm.

The configured evolutionary parameters were:

```text
Generations : 15
Population  : 10
Elite       : 1
Crossover   : 60%
Mutation    : 5%
```

Each individual in the population represents a candidate set of neural-network weights.

## Evolutionary Cycle

The optimisation process follows the general sequence:

```text
Create Random Population
          |
          v
Select Individual
          |
          v
Send Neural Weights
to Robot Controller
          |
          v
Run Simulation
          |
          v
Measure Fitness
          |
          v
Evaluate Population
          |
          v
Rank Individuals
          |
          v
Preserve Elite
          |
          v
Parent Selection
          |
          v
Crossover
          |
          v
Mutation
          |
          v
New Generation
          |
          +---------> Repeat
```

At the end of each generation, the best-performing genotype is retained.

## Selection

The genetic-algorithm framework uses tournament-style parent selection.

A subset of candidate individuals is selected and ranked according to fitness, with the strongest candidate becoming a parent.

This provides selection pressure toward higher-performing neural-network controllers.

## Crossover

Crossover combines genetic information from two parent controllers.

The implementation uses a central crossover point:

```text
Parent A:  A A A A | A A A A
Parent B:  B B B B | B B B B
                     |
                     v
Child:     A A A A | B B B B
```

The configured crossover rate for this project was 60%.

## Mutation

Following crossover, individual genes have a probability of mutation.

The configured mutation rate was:

```text
5%
```

A mutation adds a random value between -1 and 1 to the selected gene, with the resulting value constrained to the valid range.

Mutation introduces additional variation into the population and allows the evolutionary search to explore new candidate controllers.

## Elitism

The highest-performing individual is preserved when constructing the next generation.

This prevents the best solution discovered during one generation from automatically being lost through crossover or mutation.

## Genotype Evaluation

Each genotype is evaluated within the Webots simulation.

The Supervisor:

1. Sends the candidate neural-network weights to the robot.
2. Resets the robot and environment.
3. Runs the simulation for a fixed evaluation period.
4. Receives the resulting fitness.
5. Repeats the trial.
6. Calculates the mean fitness.
7. Stores the result for evolutionary selection.

The original configuration evaluates each individual over repeated trials to reduce dependence on a single simulation run.

## Robot/Supervisor Communication

The robot controller and Supervisor communicate using Webots emitter and receiver devices.

```text
Supervisor
    |
    | Neural-network weights
    v
  Robot
    |
    | Fitness
    v
Supervisor
```

The robot first reports the number of neural-network weights required by its selected architecture.

The Supervisor can then generate correctly sized genotypes and transmit candidate weight sets for evaluation.

## Best Controller

At the end of each generation, the highest-performing genotype is identified.

Its neural-network weights are saved as:

```text
Best.npy
```

The Supervisor also provides a demonstration mode that reloads this genotype and runs the evolved controller within the simulation.

This separates:

```text
TRAINING
   |
   v
Genetic Algorithm
   |
   v
Best.npy
   |
   v
DEMONSTRATION
```

## Fitness Visualisation

The Supervisor uses the Webots display interface to plot:

- Best population fitness
- Average population fitness

across generations.

This provides visual feedback on the progress of the evolutionary process.

## Concepts Demonstrated

This project provided practical experience with:

- Evolutionary robotics
- Genetic algorithms
- Neural networks
- Neuroevolution
- Fitness-function design
- Population-based optimisation
- Tournament selection
- Crossover
- Mutation
- Elitism
- Sensor normalisation
- Differential-drive control
- Autonomous behaviour
- Robot simulation
- Webots controllers
- Supervisor/robot communication
- Experimental evaluation
- Optimisation visualisation

## Code Provenance

This coursework was developed using a laboratory framework supplied during the module.

The repository therefore contains a combination of:

- Supplied laboratory framework code
- Parameters configured for the project
- Sections modified for the required robot behaviour
- Fitness-function development
- Simulation-specific modifications

Comments retained within the source identify sections inherited from or modified from the original laboratory code.

The neural-network implementation in `mlp.py` is attributed in the original source to Nicolas P. Rougier and is distributed under the BSD licence. Its original attribution and licence header have been retained.

The repository is presented transparently as an example of adapting and extending an existing robotics and evolutionary-computation framework rather than claiming the complete framework as original work.

## My Contribution

My work on the project included configuring and adapting the supplied framework for the required robot and task.

This included work such as:

- Selecting the neural-network architecture
- Configuring the network as 11 inputs, 10 hidden neurons and 2 outputs
- Integrating the required robot sensor inputs
- Normalising sensor measurements
- Configuring the genetic-algorithm parameters
- Setting crossover probability
- Setting mutation probability
- Developing and modifying the multi-objective fitness function
- Configuring the simulation for the robot
- Adapting reset behaviour for the simulation environment
- Evaluating evolved controllers

The original source comments have been retained to distinguish these modifications from supplied laboratory code.

## Retrospective

This project represents a significant progression from my earlier rule-based and manually programmed robot controllers.

The central difference is that the final motor behaviour is not explicitly programmed.

Instead:

```text
Traditional Controller

Sensors
   |
   v
Hand-Written Rules
   |
   v
Motors


Evolutionary Controller

Sensors
   |
   v
Neural Network
   |
   v
Motors
   ^
   |
Weights Evolved
by Genetic Algorithm
```

This introduced several important challenges.

### Fitness-Function Design

A genetic algorithm optimises what is measured rather than necessarily what the developer intended.

Designing the fitness function therefore becomes a critical part of designing the robot behaviour.

Rewarding forward speed alone could encourage undesirable behaviour such as collisions, while excessively penalising proximity readings could result in a controller that avoids movement.

The combined fitness function attempts to balance these competing objectives.

### Neural-Network Architecture

The original project uses a relatively small network:

```text
11 -> 10 -> 2
```

This is appropriate for demonstrating neuroevolution while keeping the genotype and evolutionary search space manageable.

With my current experience, I would evaluate multiple architectures systematically rather than selecting a single architecture manually.

### Experimental Methodology

A stronger modern implementation would run substantially more trials and record results programmatically.

Metrics could include:

- Best fitness per generation
- Mean population fitness
- Fitness variance
- Collision count
- Distance travelled
- Line-following error
- Completion rate
- Performance across multiple random seeds

This would make it easier to determine whether improvements represented genuine controller learning rather than variation between individual simulation runs.

### Genetic Algorithm

The original GA provides the fundamental evolutionary operators required for the coursework.

A modern implementation could investigate alternative:

- Selection strategies
- Crossover operators
- Mutation schedules
- Population sizes
- Elitism levels
- Stopping criteria

and compare their effect experimentally.

### Software Structure

The robot controller currently combines sensing, neural-network execution, fitness calculation and Supervisor communication.

A larger robotics system would separate these responsibilities into dedicated components.

## Portfolio Context

This project is particularly relevant to my progression into robotics and autonomous systems because it combines several areas that appear separately in my earlier work:

```text
       Python Programming
               |
               +
               |
      Robot Simulation
               |
               +
               |
        Sensor Processing
               |
               +
               |
       Neural Networks
               |
               +
               |
     Genetic Algorithms
               |
               v
      EVOLUTIONARY
        ROBOTICS
```

It demonstrates experience with an alternative approach to autonomous control in which useful behaviour emerges through optimisation rather than being completely specified through hand-written control rules.

The project also provided practical experience in one of the central challenges of autonomous systems: defining an objective that causes an optimisation process to produce the behaviour actually desired.
