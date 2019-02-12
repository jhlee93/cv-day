# CV-DAY
###### jaehyeon lee, dongho hwang, cheonghwa kim, songwon lim

## Face Recognition
<pre><code>haarcascade_frontalface_default.xml</pre></code>
- - -

## Facial Expression Recognition
#### Datasets
1. Download "fer2013.csv"
<pre><code> https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data</pre></code>

2. Datasets Form
<pre><code> 2.1. emotion(0~6)
      0 -> Angry
      1 -> Disgust
      2 -> Fear
      3 -> Happy
      4 -> Sad
      5 -> Surprise
      6 -> Neutral

  2.2. pixels value(Binary image 48x48)

  2.3. usages(Training/PrivateTest/PublicTest)</pre></code>

3. Split Datasets
<pre><code>$ git clone https://github.com/jhlee93/cv-day.git

Place "fer2013.csv" near "split_data.py".

$ python split_data.py</pre></code>

#### How to use FERModule ?
1. setting [fer.py] path
2. FERModule Definition [FERM = FERMoudle()]
3. Load Network [FERM.load_network()]
4. Run [FERM.run()]
5. Result Dictionary
6. Example
    <pre><code>result = FERM.run()
    result = {'best': 'neutral',
              'angry': '13.68',
              'disgust': '0.00',
              'scared': '20.48',
              'happy': '1.13',
              'sad': '6.43',
              'surprised': '0.91',
              'neutral':'57.38'}</pre></code>
- - -
## Cycle GAN
<pre><code>~~~</pre></code>
