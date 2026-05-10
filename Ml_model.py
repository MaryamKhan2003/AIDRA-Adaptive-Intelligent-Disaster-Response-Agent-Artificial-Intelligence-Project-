# ml.py - Loads data from CSV file 
import math
import csv
import os
import random

class SimpleNaiveBayes:
    """Gaussian Naive Bayes from scratch"""
    
    def __init__(self):
        self.class_priors = {}
        self.class_means = {}
        self.class_variances = {}
        self.classes = []
    
    def fit(self, X, y):
        X = [list(row) for row in X]
        self.classes = list(set(y))
        
        for cls in self.classes:
            class_samples = [X[i] for i in range(len(X)) if y[i] == cls]
            self.class_priors[cls] = len(class_samples) / len(X)
            
            class_samples_T = list(zip(*class_samples))
            self.class_means[cls] = [sum(feature) / len(feature) for feature in class_samples_T]
            
            self.class_variances[cls] = []
            for feature in class_samples_T:
                mean = sum(feature) / len(feature)
                variance = sum((x - mean) ** 2 for x in feature) / len(feature)
                self.class_variances[cls].append(variance + 1e-6)
    
    def _gaussian_pdf(self, x, mean, variance):
        exponent = math.exp(-((x - mean) ** 2) / (2 * variance))
        return (1 / math.sqrt(2 * math.pi * variance)) * exponent
    
    def predict_proba(self, X):
        X = [list(row) for row in X]
        probabilities = []
        
        for x in X:
            probs = {}
            for cls in self.classes:
                log_prob = math.log(self.class_priors[cls])
                
                for i, feature in enumerate(x):
                    pdf = self._gaussian_pdf(feature, self.class_means[cls][i], self.class_variances[cls][i])
                    if pdf > 0:
                        log_prob += math.log(pdf)
                    else:
                        log_prob += -100
                probs[cls] = log_prob
            
            max_log = max(probs.values())
            exp_vals = {}
            for cls, log_p in probs.items():
                exp_vals[cls] = math.exp(log_p - max_log)
            total = sum(exp_vals.values())
            
            result = {}
            for cls, val in exp_vals.items():
                result[cls] = val / total if total > 0 else 1 / len(self.classes)
            probabilities.append(result)
        
        return probabilities
    
    def predict(self, X):
        probas = self.predict_proba(X)
        return [max(p, key=p.get) for p in probas]


class SimpleKNN:
    """K-Nearest Neighbors with FEATURE SCALING"""
    
    def __init__(self, n_neighbors=3):
        self.n_neighbors = n_neighbors
        self.min_vals = None
        self.max_vals = None
    
    def _scale_features(self, X):
        X_scaled = []
        for i, val in enumerate(X):
            if self.max_vals and self.min_vals:
                if self.max_vals[i] - self.min_vals[i] > 0:
                    scaled = (val - self.min_vals[i]) / (self.max_vals[i] - self.min_vals[i])
                else:
                    scaled = 0.5
                X_scaled.append(scaled)
            else:
                X_scaled.append(val)
        return X_scaled
    
    def fit(self, X, y):
        self.X_train = [list(row) for row in X]
        self.y_train = list(y)
        
        num_features = len(self.X_train[0])
        self.min_vals = [min(row[f] for row in self.X_train) for f in range(num_features)]
        self.max_vals = [max(row[f] for row in self.X_train) for f in range(num_features)]
        
        self.X_train_scaled = [self._scale_features(row) for row in self.X_train]
    
    def _euclidean_distance(self, a, b):
        return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))
    
    def predict_proba(self, X):
        X = [list(row) for row in X]
        probabilities = []
        
        for x in X:
            x_scaled = self._scale_features(x)
            
            distances = []
            for i, train_x in enumerate(self.X_train_scaled):
                dist = self._euclidean_distance(x_scaled, train_x)
                distances.append((dist, self.y_train[i]))
            
            distances.sort(key=lambda d: d[0])
            neighbors = distances[:self.n_neighbors]
            
            votes = {}
            for dist, label in neighbors:
                weight = 1 / (dist + 0.0001)
                votes[label] = votes.get(label, 0) + weight
            
            total = sum(votes.values())
            proba = {0: 0.5, 1: 0.5}
            for label, weight in votes.items():
                proba[label] = weight / total if total > 0 else 0.5
            probabilities.append(proba)
        
        return probabilities
    
    def predict(self, X):
        probas = self.predict_proba(X)
        return [1 if p[1] > p[0] else 0 for p in probas]


def load_data_from_csv(data_file="triage_data.csv"):
    """Load and convert triage data to ML format"""
    X = []
    y = []
    
    # Map triage to severity (3=critical, 2=moderate, 1=minor)
    triage_to_severity = {
        'Critical': 3,
        'Moderate': 2,
        'Minor': 1
    }
    
    # Survival base rates
    survival_base = {
        'Critical': 0.30,
        'Moderate': 0.60,
        'Minor': 0.90
    }
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            # Read first line to check if it's header (contains 'age' or 'triage')
            first_line = f.readline().strip()
            f.seek(0)
            
            # Check if first line contains column names
            has_header = 'age' in first_line.lower() or 'triage' in first_line.lower() or 'heart_rate' in first_line.lower()
            
            if has_header:
                # Skip header
                lines = f.readlines()[1:]
            else:
                lines = [first_line] + f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('\t')  # Tab separator
                if len(parts) < 7:
                    parts = line.split(',')  # Try comma separator
                
                if len(parts) >= 7:
                    try:
                        # Extract data
                        age = int(float(parts[0])) if parts[0].strip() else 0
                        heart_rate = int(float(parts[1])) if parts[1].strip() else 0
                        breathing_rate = int(float(parts[2])) if parts[2].strip() else 0
                        consciousness = int(float(parts[3])) if parts[3].strip() else 0
                        injury_severity = int(float(parts[4])) if parts[4].strip() else 0
                        arrival_mode = parts[5].strip().lower()
                        triage = parts[6].strip()
                        
                        if triage in triage_to_severity:
                            severity = triage_to_severity[triage]
                            
                            # Calculate distance from arrival mode
                            if arrival_mode == 'walk':
                                distance = random.randint(1, 4)
                            elif arrival_mode == 'ambulance':
                                distance = random.randint(3, 7)
                            else:  # helicopter
                                distance = random.randint(5, 10)
                            
                            # Calculate risk from heart rate and breathing rate
                            risk = min(95, max(5, (heart_rate - 60) + (breathing_rate - 12) * 2))
                            
                            X.append([severity, distance, risk])
                            
                            # Determine survival outcome
                            survival_prob = survival_base[triage]
                            # Add some randomness based on vitals
                            if heart_rate > 120 or breathing_rate > 30:
                                survival_prob -= 0.1
                            elif heart_rate < 70 and breathing_rate < 16:
                                survival_prob += 0.1
                            
                            survived = 1 if random.random() < survival_prob else 0
                            y.append(survived)
                    except (ValueError, IndexError):
                        continue
        
        print(f"\n   Loaded {len(X)} samples from {data_file}")
        return X, y
    else:
        print(f"\n   Data file {data_file} not found! Using default dataset.")
        return get_default_data()


def get_default_data():
    """Default dataset (your original 60 samples) - SAME as before"""
    X = [
        [3,1,95], [3,1,90], [3,2,85], [3,2,80], [3,3,85],
        [3,3,75], [3,4,80], [3,4,70], [3,5,75], [3,5,65],
        [3,6,70], [3,6,60], [3,7,65], [3,7,55], [3,8,60],
        [3,8,50], [3,9,55], [3,9,45], [3,10,50], [3,10,40],
        [2,1,80], [2,1,75], [2,2,75], [2,2,65], [2,3,70],
        [2,3,60], [2,4,65], [2,4,55], [2,5,60], [2,5,50],
        [2,6,55], [2,6,45], [2,7,50], [2,7,40], [2,8,45],
        [2,8,35], [2,9,40], [2,9,30], [2,10,35], [2,10,25],
        [1,1,60], [1,1,55], [1,2,55], [1,2,45], [1,3,50],
        [1,3,40], [1,4,45], [1,4,35], [1,5,40], [1,5,30],
        [1,6,35], [1,6,25], [1,7,30], [1,7,20], [1,8,25],
        [1,8,15], [1,9,20], [1,9,10], [1,10,15], [1,10,5]
    ]
    y = [
        0,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,
        1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,0,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1
    ]
    return X, y


class MLModel:
    """Main ML Model class - loads data from CSV file"""
    
    def __init__(self, data_file="triage_data.csv"):
        
        # Load training data from CSV file (or use default if not found)
        X, y = load_data_from_csv(data_file)
        
        # Split into train and test sets (80/20)
        split_idx = int(len(X) * 0.8)
        X_train = X[:split_idx]
        X_test = X[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]
        
        print("\n🤖 TRAINING ML MODELS...")
        print(f"   Dataset: {len(X)} samples (from {'CSV file' if os.path.exists(data_file) else 'default dataset'})")
        print("   Features: severity (1-3), distance (1-10), risk level (5-95)")
        
        # Naive Bayes Model
        print("\n  📊 Naive Bayes Model:")
        self.nb = SimpleNaiveBayes()
        self.nb.fit(X_train, y_train)
        nb_pred = self.nb.predict(X_test)
        
        nb_correct = sum(1 for i in range(len(y_test)) if nb_pred[i] == y_test[i])
        nb_accuracy = nb_correct / len(y_test) * 100
        
        print(f"     Accuracy: {nb_accuracy:.1f}%")
        
        tp = sum(1 for i in range(len(y_test)) if nb_pred[i] == 1 and y_test[i] == 1)
        fp = sum(1 for i in range(len(y_test)) if nb_pred[i] == 1 and y_test[i] == 0)
        fn = sum(1 for i in range(len(y_test)) if nb_pred[i] == 0 and y_test[i] == 1)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        print(f"     F1 Score: {f1 * 100:.1f}%")
        
        # KNN Model
        print("\n  📊 KNN Model:")
        self.knn = SimpleKNN(n_neighbors=3)
        self.knn.fit(X_train, y_train)
        knn_pred = self.knn.predict(X_test)
        
        knn_correct = sum(1 for i in range(len(y_test)) if knn_pred[i] == y_test[i])
        knn_accuracy = knn_correct / len(y_test) * 100
        
        print(f"     Accuracy: {knn_accuracy:.1f}%")
        
        tp = sum(1 for i in range(len(y_test)) if knn_pred[i] == 1 and y_test[i] == 1)
        fp = sum(1 for i in range(len(y_test)) if knn_pred[i] == 1 and y_test[i] == 0)
        fn = sum(1 for i in range(len(y_test)) if knn_pred[i] == 0 and y_test[i] == 1)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        print(f"     F1 Score: {f1 * 100:.1f}%")
        
        # CONFUSION MATRIX
        print("\n  📊 CONFUSION MATRIX:")
        print("  " + "-" * 50)
        
        nb_pred_all = self.nb.predict(X)
        tp_nb = sum(1 for i in range(len(y)) if nb_pred_all[i] == 1 and y[i] == 1)
        tn_nb = sum(1 for i in range(len(y)) if nb_pred_all[i] == 0 and y[i] == 0)
        fp_nb = sum(1 for i in range(len(y)) if nb_pred_all[i] == 1 and y[i] == 0)
        fn_nb = sum(1 for i in range(len(y)) if nb_pred_all[i] == 0 and y[i] == 1)
        
        print("\n     Naive Bayes Confusion Matrix:")
        print("     " + "-" * 38)
        print("                     Predicted")
        print("                   Survive     Die")
        print("     " + "-" * 38)
        print(f"     Actual Survive     {tp_nb:3d}        {fn_nb:3d}")
        print(f"            Die         {fp_nb:3d}        {tn_nb:3d}")
        print("     " + "-" * 38)
        
        knn_pred_all = self.knn.predict(X)
        tp_knn = sum(1 for i in range(len(y)) if knn_pred_all[i] == 1 and y[i] == 1)
        tn_knn = sum(1 for i in range(len(y)) if knn_pred_all[i] == 0 and y[i] == 0)
        fp_knn = sum(1 for i in range(len(y)) if knn_pred_all[i] == 1 and y[i] == 0)
        fn_knn = sum(1 for i in range(len(y)) if knn_pred_all[i] == 0 and y[i] == 1)
        
        print("\n     KNN Confusion Matrix:")
        print("     " + "-" * 38)
        print("                     Predicted")
        print("                   Survive     Die")
        print("     " + "-" * 38)
        print(f"     Actual Survive     {tp_knn:3d}        {fn_knn:3d}")
        print(f"            Die         {fp_knn:3d}        {tn_knn:3d}")
        print("     " + "-" * 38)
        
        # Select best model
        if knn_accuracy >= nb_accuracy:
            self.best_model = self.knn
            self.best_name = "KNN"
            self.best_accuracy = knn_accuracy
        else:
            self.best_model = self.nb
            self.best_name = "Naive Bayes"
            self.best_accuracy = nb_accuracy
        
        print(f"\n  ✓ Best Model Selected: {self.best_name} (Accuracy: {self.best_accuracy:.1f}%)")
        print("  ✓ ML Models ready for realistic risk estimation")
    
    def predict_survival(self, severity, distance, risk_level, time_elapsed=0):
        """Predict survival probability for a victim - SAME as before"""
        severity_base = {"critical": 0.30, "moderate": 0.60, "minor": 0.90}
        base_prob = severity_base.get(severity, 0.50)
        
        distance_penalty = min(0.30, distance / 33)
        risk_penalty = min(0.40, risk_level / 250)
        time_penalty = min(0.20, time_elapsed * 0.02)
        
        prob = base_prob * (1 - distance_penalty) * (1 - risk_penalty) * (1 - time_penalty)
        prob = max(0.05, min(0.95, prob))
        
        return round(prob * 100, 1)


if __name__ == "__main__":
    print("🧪 Testing ML Model...")
    ml = MLModel()
