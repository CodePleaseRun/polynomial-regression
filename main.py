import sys
import sympy as sp
import numpy as np
import statistics as st
from fractions import Fraction
import matplotlib.pyplot as plt
from calcuate_coef import interpolate
from matplotlib.widgets import Slider, Button


class Iipn:
    def __init__(self) -> None:
        self.degree = 1
        self.fig, self.ax = plt.subplots()
        self.points, = self.ax.plot([], [], 'o', label='_nolegend_')
        self.fit_curve,  = plt.plot([], [], 'g')
        self.conf_95 = self.ax.fill_between([], [], [])
        self.conf_99 = self.ax.fill_between([], [], [])
        self.data = np.array([[], []], dtype=np.float64)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        init_plot()
        create_reset()


def create_title(coef: np.ndarray) -> str:
    '''
    Convert float cooeficient (upto 6 decimal places) into rational form  
    '''
    if len(coef) != 0:
        try:
            f = [Fraction(i).limit_denominator(1000000) for i in coef][::-1]
        except ValueError:
            return ''
        s = ''
        for index, i in enumerate(f):
            s += f'{i}*x^{index}+'
        s = s[:-1]
        s = f'${sp.latex(sp.sympify(s, convert_xor=True))}$'
        s = f'f(x) = {s};(Remaining coefficients are < '+'$\\frac{1}{10^6}$)\n'
    else:
        s = ''
    return s


def update_plot(iipn: Iipn) -> None:
    '''
    Calls clear_canvas to removes all existing matplotlib.lines.Line2D.
    Then recalculates everything to plot with updated values.
    update_plot() gets called whenever:
        1. New values are added (onclick())
        2. Degree of curve is changed (update_degree())
        3. Initial values are loaded from a file (load_points())
    '''
    clear_canvas(iipn)
    iipn.points.set_data(iipn.data[0], iipn.data[1])
    coef = interpolate(iipn.data, iipn.degree)
    coef = np.flip(coef)
    err_m, err_s = inference(coef, iipn.data)
    s = create_title(coef)
    s += f'Distance of points from f(x): $\mu$ = {err_m:5f},$\sigma$ = {err_s:5f}'
    iipn.ax.set_title(s, fontsize=17)
    x, y = get_fit_curve(coef, iipn.data)
    iipn.fit_curve, = iipn.ax.plot(x, y, 'g')
    iipn.conf_95 = iipn.ax.fill_between(
        x, y+2*err_s, y-2*err_s, alpha=0.2, color='b')
    iipn.conf_99 = iipn.ax.fill_between(
        x, y+3*err_s, y-3*err_s, alpha=0.1, color='r')
    iipn.ax.legend(['Interpolation', '95% Interval', '99% Interval'])
    plt.draw()


def update_degree(val: int, iipn: Iipn) -> None:
    '''
    Changes the value of iipin.degree to the value slider is on. Invokes update_plot to plot the new curve
    '''
    iipn.degree = val
    update_plot(iipn)


def clear_canvas(iipn: Iipn, clear_all: bool = False) -> None:
    '''
    By default, removes all existing matplotlib.lines.Line2D
    if clear_all == True, then deletes all the existing data points from iipin.data
    '''
    try:
        iipn.fit_curve.remove()
        iipn.conf_95.remove()
        iipn.conf_99.remove()
    except:
        pass
    if clear_all:
        iipn.data = np.array([[], []], dtype=np.float64)
        iipn.points.set_data(iipn.data[0], iipn.data[1])
        iipn.ax.set_xlim(0, 100)
        iipn.ax.set_ylim(0, 100)
        plt.draw()


def init_plot() -> None:
    plt.grid()
    plt.tight_layout()
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()


def create_slider(max_degree: int) -> Slider:
    '''
    Creates the slider used for changing degree.
    Also adjust the heigh of subplot to make room for title & slider
    '''
    plt.subplots_adjust(bottom=0.10)
    plt.subplots_adjust(top=0.90)
    ax_silder = plt.axes([0.3, 0.025, .5, 0.04])
    degree_slider = Slider(ax_silder, "Degree", 0, max_degree,
                           initcolor='none', valinit=1, valstep=1, color="green")
    return degree_slider


def load_points(file_name: str, iipn: Iipn) -> None:
    '''
    Loads data points (one point 'x,y\n' in each line) from a file.
    Changes set_xlim and set_xlim of iipin.ax to auto
    '''
    try:
        with open(file_name) as data:
            coord = data.readlines()
    except FileNotFoundError:
        print(f'{file_name} not found.\n')
        quit()
    try:
        coord = [[float(k) for k in i.strip().split(',')] for i in coord]
    except ValueError:
        print('Float conversion failed.\n')
        quit()
    x_coord = [i[0] for i in coord]
    y_coord = [i[-1] for i in coord]
    iipn.data = np.array([x_coord, y_coord], dtype=np.float64)
    iipn.ax.set_xlim(auto=True)
    iipn.ax.set_ylim(auto=True)
    update_plot(iipn)


def create_reset() -> Button:
    '''
    Creates the reset button
    '''
    ax_reset = plt.axes([0.9, 0.025, 0.05, 0.04])
    button = Button(ax_reset, 'Reset', hovercolor='0.975')
    return button


def onclick(event, iipn: Iipn) -> None:
    '''
    Event handling function
    '''
    if not event.dblclick:
        return
    if not event.inaxes:
        return
    x_val = event.xdata
    y_val = event.ydata
    iipn.data = np.append(iipn.data, [[x_val], [y_val]], axis=1)
    update_plot(iipn)


def get_fit_curve(coef: np.ndarray, data: np.ndarray) -> tuple:
    '''
    Calculates all the points of the fitting curve
    '''
    x = np.linspace(min(data[0]), max(data[0]), 1000)
    y = np.polyval(coef, x)
    return (x, y)


def inference(coef: np.ndarray, data: np.ndarray) -> tuple:
    '''
    Calculates the mean and stdev of vertical distance of all points about fitting curve
    '''
    y_dash = np.polyval(coef, data[0])
    abs_error = np.abs(data[1]-y_dash)
    error_mean = st.mean(abs_error)
    try:
        error_sd = st.stdev(abs_error)
    except st.StatisticsError:
        error_sd = 0
    return (error_mean, error_sd)


def init_main(iipn: Iipn) -> None:
    '''
    Initializes slider, reset button & event handler
    '''
    degree_slider = create_slider(max_degree=30)
    reset_button = create_reset()
    reset_button.on_clicked(lambda x: clear_canvas(iipn=iipn, clear_all=True))
    degree_slider.on_changed(lambda x: update_degree(val=x, iipn=iipn))
    cid = iipn.fig.canvas.mpl_connect(
        'button_press_event', lambda x: onclick(x, iipn))
    plt.show()


if __name__ == '__main__':
    iipn = Iipn()
    try:
        file_name = sys.argv[1]
        load_points(file_name, iipn)
    except IndexError:
        pass
    init_main(iipn)
