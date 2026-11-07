"""Interview quiz questions for the technical roles added in Phase 4."""


def _q(qid, topic, prompt, options, answer):
    return {"id": qid, "topic": topic, "prompt": prompt, "options": options, "answer": answer}


EXTRA_BANKS = {
    "ml_engineer": [
        _q("ml-1", "Overfitting", "A model scores 99% on its training data but 70% on new data. What is the most likely problem?",
           ["Underfitting", "A bug in the plotting library", "Overfitting", "Too many classes"], 2),
        _q("ml-2", "Train/test split", "Why do we keep a separate test set?",
           ["To make training faster", "To estimate how the model performs on unseen data",
            "To increase the amount of training data", "To remove outliers"], 1),
        _q("ml-3", "Classification metrics",
           "A dataset has 99% negative examples. Which metric can look excellent even for a model that never predicts positive?",
           ["Precision", "Recall", "F1 score", "Accuracy"], 3),
        _q("ml-4", "Gradient descent", "What does gradient descent do?",
           ["Sorts the training data", "Splits data into folds", "Removes missing values",
            "Iteratively adjusts parameters to reduce the loss"], 3),
        _q("ml-5", "Feature scaling", "Which algorithm is most sensitive to the scale of its input features?",
           ["Decision tree", "Random forest", "k-nearest neighbours", "Gradient-boosted trees"], 2),
        _q("ml-6", "Cross-validation", "What is k-fold cross-validation used for?",
           ["Speeding up inference", "Reducing the number of features", "Encoding categorical data",
            "Estimating performance more reliably using several train/validation splits"], 3),
    ],
    "cloud_devops": [
        _q("cd-1", "Containers vs VMs", "Compared with a virtual machine, a container typically:",
           ["Includes its own full guest operating system", "Shares the host operating system kernel and starts faster",
            "Cannot run on Linux", "Needs a hypervisor for each process"], 1),
        _q("cd-2", "CI/CD", "What is the main goal of continuous integration?",
           ["Deploy to production only once a year", "Replace version control",
            "Merge and automatically test code changes frequently", "Write documentation automatically"], 2),
        _q("cd-3", "Infrastructure as code", "What is Infrastructure as Code?",
           ["Writing code that runs on a server", "A programming language for web pages", "A type of cloud billing plan",
            "Managing infrastructure through versioned configuration files"], 3),
        _q("cd-4", "Linux permissions", "What does chmod 755 give the file's owner?",
           ["Read only", "Read, write and execute", "Execute only", "No permissions"], 1),
        _q("cd-5", "Kubernetes", "In Kubernetes, what is a Pod?",
           ["A physical server", "A container image registry",
            "The smallest deployable unit, running one or more containers", "A type of network firewall"], 2),
        _q("cd-6", "Availability", "What is the main benefit of running an application across several availability zones?",
           ["Lower storage costs", "Faster code compilation", "Automatic unit tests",
            "Higher availability if one zone fails"], 3),
    ],
    "cybersecurity": [
        _q("cy-1", "CIA triad", "In the CIA triad, what does the 'I' stand for?",
           ["Identity", "Integrity", "Inspection", "Isolation"], 1),
        _q("cy-2", "Phishing", "An email that pretends to be your bank to steal your password is an example of:",
           ["Port scanning", "Denial of service", "Phishing", "A brute-force login"], 2),
        _q("cy-3", "SQL injection", "What is the best primary defence against SQL injection?",
           ["Hiding the database port", "Longer passwords", "Using HTTPS only", "Parameterised queries"], 3),
        _q("cy-4", "Encryption", "Which kind of encryption uses the same key to encrypt and to decrypt?",
           ["Asymmetric encryption", "Symmetric encryption", "Hashing", "A digital signature"], 1),
        _q("cy-5", "Ports and protocols", "Which port does HTTPS use by default?",
           ["80", "22", "443", "3389"], 2),
        _q("cy-6", "Least privilege", "The principle of least privilege means:",
           ["Users get only the access they need to do their job", "Everyone shares one admin account",
            "Passwords never expire", "All traffic is encrypted twice"], 0),
    ],
}