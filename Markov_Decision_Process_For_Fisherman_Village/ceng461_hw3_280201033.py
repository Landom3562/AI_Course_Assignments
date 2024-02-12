M = 100
discount_factor = 0.9

growth_rates = [1, 1.25, 1.5, 1.75]
probabilities = [0.2, 0.3, 0.3, 0.2]

########## Value iteration algorithm ##########

utilities = [0] * (M+1) #Utilities and policies of states are stored in two arrays. 
policies = [0] * (M+1)  #For example utility of state 1 is utilities[1] and policy of state 1 is to catch policies[1] number of fish. 

converged = False #A flag to stop while loop when the difference between utilities are small enough
iteration = 0
while not converged:
    iteration += 1 #Iteration counter just for printing purposes
    next_utilities = [0] * (M+1)
    next_optimal_policies = [0] * (M+1)
    for state in range(M+1):
        max_utility = 0
        optimal_policy = 0
        for hunted_fish_count in range(state+1):
            expected_utility = 0
            for i in range(len(growth_rates)):
                next_state = min(M, int(0.5 + (state - hunted_fish_count) * growth_rates[i])) #int(0.5+x) is used to round the float numbers to the closest integer. 
                expected_utility += probabilities[i] * utilities[next_state]                  #Tried round() but it wasn't rounding 2.5 to 3.Instead it was rounding it down to 2.
            utility = hunted_fish_count + discount_factor * expected_utility
            if utility > max_utility:
                max_utility = utility
                optimal_policy = hunted_fish_count
        
        next_utilities[state] = max_utility
        next_optimal_policies[state] = optimal_policy
    
    #Checking if the utilities are converged
    total_difference = 0
    for i in range(M+1):
        total_difference += next_utilities[i] - utilities[i]
    if (total_difference < (10**-6)):
        converged = True
    
    #Updating utilities and policies 
    utilities = next_utilities 
    policies = next_optimal_policies

    print(f"ITERATION {iteration}")
    for i in range(M+1):
        print(f"\tSTATE {i}:")
        print(f"\t\tUtility of state {i} after iteration {iteration}: {utilities[i]}")
        print(f"\t\tOptimal policy of state {i} after iteration {iteration}: Catch {policies[i]} fish")


print("OPTIMAL POLICIES FOR EACH STATE:")
for i in range(M+1):
    print(f"\t State {i}: Catch {policies[i]} fish")