import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from LogParser import LogParser

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
old_f = []
lp = LogParser('config.ini')
def animate(i):
    global old_f
    with open('history.log', 'r') as f:
        new_f = f.readlines()
        if new_f != old_f:
            old_f = new_f[:]
            lp.add_log(old_f)
            lp.watson_report_cumulative()
            # Isolate x axis
            x = lp.axes['x']
            ax1.clear()
            for name, things in lp.axes.items():
                if name == 'x':
                    continue
                print(lp.axes)
                plt.plot(x, things, label=name)
                plt.legend(loc=2, prop={'size': 7})

        else:
            pass


ani = animation.FuncAnimation(fig, animate, interval=500)
plt.xlabel('Time')
plt.ylabel('Percentile')
plt.title('Sentiment analysis by percentile')

plt.show()