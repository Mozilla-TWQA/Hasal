class outlier(object):
    def detect(self, seq):
        seq.sort()
        outliers = []
        if len(seq)>=3:
            #Using Moore and McCabe method to calculate quartile value
            [median,Q1,Q3] = self.Q_MooreMcCabe(seq)
            IQR = Q3 - Q1
            lower = Q1 - 1.5*IQR
            upper = Q3 + 1.5*IQR    
            for data in seq:
                if data < lower or data > upper: outliers.append(data)
    
            self.drop(seq, outliers)
        if len(seq) == 0:
            median = 0
        elif len(seq)%2:
            median = float(seq[(len(seq)-1)/2])
        else:
            median = float(seq[len(seq)/2-1]+seq[len(seq)/2])/2
        return median, seq, outliers
        
    def Q_MooreMcCabe(self, seq):
        seq_len = len(seq)
        if seq_len%2:
            median = float(seq[(seq_len-1)/2])
            if (seq_len+1)%4:
                Q1 = float((seq[(seq_len+1)/4]+seq[(seq_len+1)/4-1]))/2
            else:
                Q1 = float(seq[(seq_len+1)/4-1])
            if (3*seq_len+3)%4:
                Q3 = float((seq[(3*seq_len+3)/4]+seq[(3*seq_len+3)/4-1]))/2
            else:
                Q3 = float(seq[(3*seq_len+3)/4-1])
        else:
            median = float(seq[seq_len/2-1]+seq[seq_len/2])/2
            if (seq_len+2)%4:
                Q1 = float((seq[(seq_len+2)/4]+seq[(seq_len+2)/4-1]))/2
            else:
                Q1 = float(seq[(seq_len+2)/4-1])
            if (3*seq_len+2)%4:
                Q3 = float((seq[(3*seq_len+2)/4]+seq[(3*seq_len+2)/4-1]))/2
            else:
                Q3 = float(seq[(3*seq_len+2)/4-1])
        return [median,Q1,Q3]
    
    def drop(self, seq, outliers):
        for outlier in outliers:
            seq.remove(outlier)
        return seq

