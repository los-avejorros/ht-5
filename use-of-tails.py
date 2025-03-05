import simpy
import random
import statistics

# --- SIMULATION PARAMETERS --- #
RANDOM_SEED = 42 # -->  SPEED FOR TANDOM NUMBER GENERATION TO ENSURE RESPRODUCIBILITY
MEMORY_RAM = 100 # --> TOTAL RAM EVAILABLE IN THE SYSTEM
ARRIVAL_INTERVAL = 10 # --> AVERAGE TIME BETWWN PROCESS ARRIVALS (EXPONENTIAL DISTRIBUTION)
CPU_SPEDD = 3 # --> NUMBER OF INSTRUCTIONS THE CPU CAN EXECUTE PER TIME UNIT
NUM_PROCESSES = 25 # --> NUMBER OF PROCESSES TO SIMULATE (50, 100, 150, 200)

# --- SET THE RANDOM SEED FOR REPRODUCIBILITY --- #
random.seed(RANDOM_SEED)

process_times = []

# --- [THE PROCESS BEHAVIOR] --- #
def process(env, name, ram, cpu, memory_needed, instructions):
  """
   Simulates the lifecycle of a process in the system.
    - env: SimPy environment
    - name: Process name/ID
    - ram: SimPy Container representing the RAM
    - cpu: SimPy Resource representing the CPU
    - memory_needed: Amount of RAM the process requires
    - instructions: Total number of instructions the process needs to execute
  """
  arrival_time = env.now # ---> RECORD THE ARRIVAL TIME
  print(f'{name} arrives in the system at time {arrival_time}')

  # @REQUEST RAM MEMORY
  with ram.get(memory_needed) as req:
    yield req # ---> wait until the required memory is available
    print(f'{name} obtains {memory_needed} RAM at time {env.now}')

    # @PROCESS ENTERS THE "READY" STATE AND WAITS FOR THE CPU
    while instructions > 0:
      with cpu.request() as req_cpu:
        yield req_cpu # --> wait until the CPU is available
        print(f'{name} start executing at time {env.now}')
        
        # @EXECUTE INSTRUCTIONS (UP TO CPU_SPEED INSTRUCTIONS PER TIME UNIT)
        executed = min(CPU_SPEDD, instructions) # --> execute up to 3 instructions
        yield env.timeout(1) # --> simulate the time token to execute the instructions
        instructions -= executed # --> update the remaining instructions
        print(f'${name} executes {executed} instructions, {instructions} remaining at time {env.now}')
        
        # @DECIDE THE NEXT STATE OF THE PROCESS
        if instructions == 0:
          # --> if no more instructions, the process terminates
          print(f'{name} terminates at time {env.now}')
          ram.put(memory_needed) # --> release the RAM memory
          total_time = env.now - arrival_time # --> calculate total time in the system
          process_times.append(total_time)  # Store the total time
          print(f'{name} spent {total_time} time units in the system')
          break
        else:
          # --> randomly decide if the process goes to "waiting" or back to "ready"
          decision = random.randint(1,2)
          if decision == 1:
            # --> process goes to "waiting" for I/O
            print(f'{name} goes to waiting at time {env.now}')
            yield env.timeout(random.randint(1,2)) # --> simulate I/O
            print(f'{name} returns ti ready at time {env.now}')
          else:
            # --> process goes back to "ready"
            print(f'{name} returns to ready at time {env.now}')

def process_generator(env, ram, cpu):
  """
    Generates processes with exponential inter-arrival times.
    - env: SimPy environment
    - ram: SimPy Container representing the RAM
    - cpu: SimPy Resource representing the CPU
  """
  for i in range(NUM_PROCESSES):
    memory_needed = random.randint(1,10) # --> random memory requirement between 1 and 10
    instructions = random.randint(1,10) # --> random number of instructions between 1 and 10
    env.process(process(env, f'Process {i}', ram,cpu, memory_needed,instructions))
    yield env.timeout(random.expovariate(1.0/ARRIVAL_INTERVAL)) # --> exponential inter-arrival time

env = simpy.Environment() # --> create the SimPy environment
ram = simpy.Container(env, init=MEMORY_RAM, capacity=MEMORY_RAM) # --> RAM as a SimPy container
cpu = simpy.Resource(env, capacity=1) # --> CPU as a SimPy Resource (capacity = 1)

# --- [START THE PROCESS GENERATOS] --- #
env.process(process_generator(env, ram, cpu))

""" || --- $[RUN SIMULATION]$ --- || """
env.run()

# --- [CALCULATE AVERAGE TIME AND STANDARD DEVIATION] --- #
if process_times:
    average_time = statistics.mean(process_times)
    std_deviation = statistics.stdev(process_times)
    print(f'Average time in system: {average_time:.2f} time units')
    print(f'Standard deviation: {std_deviation:.2f} time units')
else:
    print('No processes were executed.')
