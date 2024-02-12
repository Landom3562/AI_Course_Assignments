def read_data(data_actual_words_path, data_ocr_outputs_path):
    with open(data_actual_words_path, 'r') as f_actual, open(data_ocr_outputs_path, 'r') as f_ocr:
        actual_words = [line.strip() for line in f_actual.readlines()]
        ocr_outputs = [line.strip() for line in f_ocr.readlines()]
    return actual_words, ocr_outputs

def calculate_probabilities(actual_words, ocr_outputs):
    #Count calculations:
    word_count = len(actual_words)
    initial_state_counts = dict() #Has the letter as key and its count as its value
    transition_counts = dict() #Has a tuple for key which is in the form of (Xn|Xn-1) and its value is the count
    emission_counts = dict() #Has a tuple for key which is in the form of (En|Xn) and its value is the count
    conditioned_letter_count_in_transitions = dict() #Has the conditioned_letter(Xn-1) as key and its count as its value
    conditioned_letter_count_in_emissions = dict() #Has the conditioned_letter(Xn) as key and its count as its value
    for actual_word, ocr_output in zip(actual_words, ocr_outputs):
        for i in range(len(actual_word)):
            #Emission calculations will be done regardless of the position of the read letter.
            if (ocr_output[i], actual_word[i]) in emission_counts.keys(): #Increment the key if it exists or create a new key with the value of 1
                emission_counts[(ocr_output[i], actual_word[i])] += 1
            else:
                emission_counts[(ocr_output[i], actual_word[i])] = 1

            if actual_word[i] in conditioned_letter_count_in_emissions.keys():
                conditioned_letter_count_in_emissions[actual_word[i]] += 1
            else:
                conditioned_letter_count_in_emissions[actual_word[i]] = 1
            
            if(i == 0): #If we are reading the first letter, we just add it to initial counts.
                if actual_word[i] in initial_state_counts.keys():
                    initial_state_counts[actual_word[i]] += 1
                else:
                    initial_state_counts[actual_word[i]] = 1
            else: #If we are reading any letter that is not the first, we should increment transition counts
                if (actual_word[i], actual_word[i-1]) in transition_counts.keys():
                    transition_counts[(actual_word[i], actual_word[i-1])] += 1
                else:
                    transition_counts[(actual_word[i], actual_word[i-1])] = 1

                if actual_word[i-1] in conditioned_letter_count_in_transitions.keys():
                    conditioned_letter_count_in_transitions[actual_word[i-1]] += 1
                else:
                    conditioned_letter_count_in_transitions[actual_word[i-1]] = 1
    
    #Probability calculations:
    initial_state_probabilities = dict() #Has the letter as key and its probability as its value
    transition_probabilities = dict() #Has a tuple for key which is in the form of (Xn|Xn-1) and its value is the probability
    emission_probabilities = dict() #Has a tuple for key which is in the form of (En|Xn) and its value is the probability

    for key in initial_state_counts.keys(): #Dividing every letter's count with the total amount of words
        initial_state_probabilities[key] = initial_state_counts[key]/word_count
    
    for key in transition_counts.keys(): #Dividing every transition count with the total amount of transitions that has the conditioned letter given.
        conditioned_key = key[1]
        conditioned_count = conditioned_letter_count_in_transitions[conditioned_key]
        transition_probabilities[key] = transition_counts[key]/conditioned_count

    for key in emission_counts.keys():
        conditioned_key = key[1]
        conditioned_count = conditioned_letter_count_in_emissions[conditioned_key]
        emission_probabilities[key] = emission_counts[key]/conditioned_count

    return initial_state_probabilities, transition_probabilities, emission_probabilities

def viterbi_algorithm(ocr_output, initial_state_probabilities, transition_probabilities, emission_probabilities):
    V = [{}] #Array of dictionaries that will have the form of: V[0] will be the states in first letter and the dictionary will have the letter as key and it's probability as its value
    paths = {} #This dictionary will hold the paths that is used to reach the states. For example the path to V[3][A] will be recorded as {(3,A) : [A,B,D]}

    domain = initial_state_probabilities.keys()

    for letter in domain:#Initializing all first states and writing them to the first elem of array
        V[0][letter] = emission_probabilities.get((ocr_output[0],letter), 0) * initial_state_probabilities[letter]
        paths[(0,letter)] = []
    
    for i in range(1,len(ocr_output)):
        V.append({})
        for current_letter in domain:#Calculation of V[i][letter]
            possible_values = {} #Letter before and probability of it being the previous letter
            for previous_letter in domain:#Calculating all possible previous letters probability
                possible_values[previous_letter] = emission_probabilities.get((ocr_output[i], current_letter), 0) * transition_probabilities.get((current_letter, previous_letter), 0) * V[i-1].get(previous_letter, 0)
            max_key_value_pair = ('A', 0) #Just a placeholder for finding the key with the max value
            for key in possible_values.keys():#Finding the previous letter that has the maximum likelihood 
                if (possible_values[key] > max_key_value_pair[1]):
                    max_key_value_pair = (key,possible_values[key])
            V[i][current_letter] = max_key_value_pair[1]
            paths[(i,current_letter)] = paths[(i-1, max_key_value_pair[0])] + [max_key_value_pair[0]]
    
    ocr_length_minus_1 = len(ocr_output) - 1 #Created just because (len(ocr_output)-1) is used in more than 1 place

    max_probability_key_value_pair = ('A', 0) #To find the maximum probability ending state
    for letter in domain: #Finding the maximum probability ending state
        if(V[ocr_length_minus_1][letter] > max_probability_key_value_pair[1]):
            max_probability_key_value_pair = (letter, V[ocr_length_minus_1][letter])
    
    estimated_sequence = paths[(ocr_length_minus_1, max_probability_key_value_pair[0])] + [max_probability_key_value_pair[0]]
    estimated_word = ''.join(estimated_sequence)
    return estimated_word


def compare_words(actual_words, ocr_outputs, initial_state_probabilities, transition_probabilities, emission_probabilities):
    correct_estimations = 0
    for actual_word, ocr_output in zip(actual_words, ocr_outputs):

        estimated_word = viterbi_algorithm(ocr_output, initial_state_probabilities, transition_probabilities, emission_probabilities)

        if ocr_output != estimated_word:
            print(f"Original Word: {actual_word}, OCR Output: {ocr_output}, Estimated Word: {estimated_word}")

        for a,o,e in zip(actual_word, ocr_output, estimated_word):
            if (a != o) and (a == e):
                correct_estimations += 1
    print(f"Number of corrected letters where OCR output is wrong but estimation is correct: {correct_estimations}")


def main():
    actual_words, ocr_outputs = read_data('data_actual_words.txt', 'data_ocr_outputs.txt')

    initial_state_probabilities, transition_probabilities, emission_probabilities = calculate_probabilities(actual_words[:50000], ocr_outputs[:50000])
    print('Initial State Probabilities:')
    for key in initial_state_probabilities.keys():
        print(key,initial_state_probabilities[key])

    print('Transition Probabilities:')
    for key in transition_probabilities.keys():
        print(key,transition_probabilities[key])
    
    print('Emission Probabilities:')
    for key in emission_probabilities.keys():
        print(key,emission_probabilities[key])


    compare_words(actual_words[50000:], ocr_outputs[50000:], initial_state_probabilities, transition_probabilities, emission_probabilities)

if __name__ == "__main__":
    main()