import codecs

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


from question import Question

class MaltImporter:

    questions = [];
    
    def getRawQuestionTexts(self, qFilePath):
        qFile = codecs.open(qFilePath, 'r', 'utf-8');##utf-8 file
        qTexts = qFile.readlines();
        qTexts = [text.strip().split('|') for text in qTexts];

        return qTexts; ## list of raw questions with Focus and Mod

    def getParsedQuestionTexts(self, qParsedFilePath):
        qFile = codecs.open(qParsedFilePath, 'r', 'utf-8');
        qTexts = qFile.readlines();
        qTexts = [text.strip().split('\t') for text in qTexts];

        questions = [];
        qParts = [];

        for text in qTexts:
            if(len(text) > 1):
                if(text[1] == "."):
                    
                    qParts.append(text);
                    questions.append(qParts);
                    qParts = [];
                else:
                    qParts.append([t.replace('\ufeff', '') for t in text]);
        
        return questions;##Question parts -> list of list


    def importMaltOutputs(self, qFilePath, qParsedFilePath):
        self.questions = [];

        qTexts = self.getRawQuestionTexts(qFilePath);
        qTextParts = self.getParsedQuestionTexts(qParsedFilePath);

        length = len(qTexts);

        for i in range(0, length):
            question = Question(qTexts[i][0], qTextParts[i]);
            question.focus = qTexts[i][1];
            #question.mod = qTexts[i][2];
            question.coarseClass = qTexts[i][3];
            question.fineClass = qTexts[i][4];
            question.setMeta(qTexts[i][1], qTexts[i][2]);

            question.answer = qTexts[i][5];
            
            self.questions.append(question);
            
        return self.questions;

