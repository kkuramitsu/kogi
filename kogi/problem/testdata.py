#ex1-1
import pandas as pd
df = pd.read_csv('pollen.csv')

# test
_ = df.head()

#ex1-2
import pandas as pd
df = pd.read_csv('pollen.csv')

# test
_ = df.sort_values(by='平均気温', ascending=False)


#ex1-3
import pandas as pd
df = pd.read_csv('pollen.csv')
plt.hist(df['杉花粉飛散量'], width=0.8, color='pink')

#test 
_ = tosvg(plt)

