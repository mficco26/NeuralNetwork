import numpy as np

class Network:
    def __init__(self, layer_sizes, activation_func="relu"):
        self.layer_sizes = layer_sizes
        self.activation_func = activation_func
        self.learning_rate = 0.004
        self.weights = []
        self.biases = []
        for i in range(len(self.layer_sizes)):
            if i != 0:
                self.weights.append(np.random.standard_normal((self.layer_sizes[i], self.layer_sizes[i-1])))
                self.biases.append(np.zeros((self.layer_sizes[i],1)))

    def feedforward(self, inputs):
        #(just for when testing with non np arrays)
        if isinstance(inputs, np.ndarray) == False:
            inputs = np.array(inputs).reshape((self.layer_sizes[0],1))

        outputs = []
        for i, (w,b) in enumerate(zip(self.weights,self.biases)):
            output = np.matmul(w, inputs) + b
            if i == len(self.weights)-1:#if calculating final output, use sigmoid:
                output = self.activation(output, "sigmoid")
            else:
                output = self.activation(output, self.activation_func)
            outputs.append(output)
            inputs = output

        return outputs
        
    def calculate_errors(self, outputs, targets):
        errors = []
        errors.append(targets - outputs[-1])
        
        weights_T = list(map(np.transpose, self.weights))
        weights_T.reverse() # weights_t was going left->right, errors is going right->left      
        weights_T.pop() # first matrix of weights don't matter (we aren't calculating error of inputs)
 
        for count, wt in enumerate(weights_T):
            errors.append(np.matmul(wt, errors[count]))
        
        errors.reverse() # Errors now going left->right (helps with train)
        return errors


    def train(self, inputs, targets):
        # Convert list inputs to numpy arrays (unless already a np array)
        if isinstance(inputs, np.ndarray) == False:
            inputs = np.array(inputs).reshape((self.layer_sizes[0],1))
        if isinstance(targets, np.ndarray) == False:
            targets = np.array(targets).reshape((self.layer_sizes[-1],1))
        
        outputs = self.feedforward(inputs)
        errors = self.calculate_errors(outputs, targets)
       

        # Calculate Gradients and Deltas from left->right through layers
        gradients = []
        deltas = []
        for layer_index, (layer_output, layer_error) in enumerate(zip(outputs, errors)):
            if layer_index == len(outputs):
                layer_gradients = self.derivative(layer_output, "sigmoid")
            else:
                layer_gradients = self.derivative(layer_output, self.activation_func)
            layer_gradients *= layer_error
            layer_gradients *= self.learning_rate
            gradients.append(layer_gradients)
            
            # Transpose input of layer, and mutiply by gradient to get deltas for weights  
            if layer_index == 0:
                layer_input_T = np.transpose(inputs)
            else:
                layer_input_T = np.transpose(outputs[layer_index-1])
            
            layer_deltas = np.matmul(layer_gradients, layer_input_T)
            deltas.append(layer_deltas)


        # Update Weights by deltas
        for d in range(len(deltas)):
            self.weights[d] += deltas[d]
            
        # Update Biases by gradients
        for g in range(len(gradients)):
            self.biases[g] += gradients[g]
    

    def activation(self, x, activation_func):
        if activation_func == "sigmoid":
            x = np.clip(x, -400, 400)
            return 1/(1+np.exp(-x))
        elif activation_func == "relu":
            return np.maximum(x,0)
    def derivative(self, x, activation_func): 
        if activation_func == "sigmoid":
            return x * (1-x)
        elif activation_func == "relu":
            x[x<=0] = 0
            x[x>0] = 1
            return x
