from src import db

class AutoScalingConfig(db.Model):
    __tablename__ = 'autoScalingConfig'
    isOn = db.Column(db.Boolean, primary_key=True)
    shrink_ratio = db.Column(db.Float)
    expand_ratio = db.Column(db.Float)
    shrink_threshold = db.Column(db.Float)
    expand_threshold = db.Column(db.Float) # should expand if larger than his threshold

    def __init__(self, isOn, shrink_ratio, expand_ratio, shrink_threshold, expand_threshold):
        self.isOn = isOn
        self.shrink_ratio = shrink_ratio
        self.expand_ratio = expand_ratio
        self.shrink_threshold = shrink_threshold
        self.expand_threshold = expand_threshold

    def __repr__(self):
        return 'Config: <shrink ratio: {}, expand ratio: {}, shrink threshold: {}, expand threshold: {}>'.format(self.shrink_ratio, self.expand_ratio, self.shrink_threshold, self.expand_threshold)
