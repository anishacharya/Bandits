import numpy as np
import math
import matplotlib.pyplot as plt


class ETC:
    def __init__(self, avg: np.ndarray, explore_steps: int):

        self.true_means = avg  # true means of the arms
        self.m = explore_steps  # num of explore steps per arm

        self.time = 0
        self.regret = []

        self.emp_means = np.zeros_like(self.true_means)  # empirical means of arms
        self.num_pulls = np.zeros_like(self.true_means)  # number of times that arm i has been pulled

        self.num_arms = avg.size  # num arms (k)
        self.explore_horizon = self.m * self.num_arms

        self.best_arm = int(np.argmax(self.true_means))  # True best arm

        self.arm_ix = None

    def restart(self):
        # Reset counters
        self.time = 0
        self.regret = []
        self.emp_means = np.zeros_like(self.true_means)
        self.num_pulls = np.zeros_like(self.true_means)
        self.arm_ix = None

    def get_best_arm(self):
        # For each time index, find the best arm according to ETC.
        return np.argmax(self.emp_means)

    def update_stats(self, rew_vec):
        ni = self.num_pulls[self.arm_ix]

        # genie plays best arm
        genie_rew = rew_vec[self.best_arm]
        player_rew = rew_vec[self.arm_ix]
        self.regret.append((genie_rew - player_rew))

        if self.time < self.m * self.num_arms:
            # keep online average
            self.emp_means[self.arm_ix] = self.emp_means[self.arm_ix] * (ni / (ni + 1)) + player_rew / (ni + 1)

        self.num_pulls[self.arm_ix] += 1
        self.time += 1

    def get_reward(self):
        return self.true_means + np.random.normal(0, 1, np.shape(self.true_means))

    def iterate(self):
        rew_vec = self.get_reward()

        if self.time < self.explore_horizon:
            # Explore Phase - Round Robin
            self.arm_ix = self.time % self.num_arms

        elif self.time == self.explore_horizon:
            # calculate best arm explored empirical
            self.arm_ix = self.get_best_arm()

        self.update_stats(rew_vec=rew_vec)


def run(avg, explore_steps, iterations, num_repeat):
    regret = np.zeros((num_repeat, iterations))
    etc = ETC(avg=avg, explore_steps=explore_steps)
    for j in range(num_repeat):
        np.random.seed(j)
        for t in range(iterations):
            etc.iterate()

        # calculate cumulative regret
        regret[j, :] = np.cumsum(np.asarray(etc.regret))
        etc.restart()

    return regret


if __name__ == '__main__':
    mu = np.asarray([0.6, 0.9, 0.95, 0.8, 0.7, 0.3])
    num_iter, num_inst = int(1e4), 30

    delta = 0.2
    m = max(1, math.ceil((4 / delta ** 2) * math.log(num_iter * (delta ** 2 / 4))))
    reg = run(avg=mu,
              explore_steps=m,
              iterations=num_iter,
              num_repeat=num_inst)

    mean_runs = np.mean(reg, axis=0)
    std_runs = np.std(reg, axis=0)

    UB = mean_runs + 1 * std_runs
    LB = mean_runs - 1 * std_runs

    x = np.arange(len(mean_runs))
    plt.plot(x, mean_runs, color='b')
    plt.fill_between(x, LB, UB, alpha=0.3, linewidth=0.5, color='b')
    
    plt.vlines(x=m*len(mu), ymin=0, ymax=1000, linestyle='dashed', color='k')
    plt.xlabel('Time', fontsize=10)
    plt.ylabel('Cumulative Regret', fontsize=10)
    plt.grid(True, which='both', linestyle='--')
    plt.show()
