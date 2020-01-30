from bandit import Bandit
import matplotlib.pyplot as plt
import numpy as np


def average_reward(Q, N):
  return np.dot(Q, N) / sum(N)


def constant_alpha(alpha=0.1):
  return lambda x: alpha


def sample_average(N):
  return (1/N)


def a_simple_bandit_algorithm(bandit, n_iterations=1000, eps=0.1,
                              weight_fn=sample_average, random_walk=False,
                              Q_1=0):
  """Returns the estimated Q-Values of the bandit problem."""
  k, q = bandit.k, bandit.q
  Q, N, R_log = np.zeros(k) + Q_1, np.zeros(k), np.zeros(k)
  avg_rew, distance_to_true_q = [], []
  for _ in range(n_iterations):
    if np.random.random() < eps:
      A = np.random.choice(k)
    else:
      A = np.random.choice(np.flatnonzero(Q == Q.max()))
    R = bandit.reward(A)
    N[A] += 1
    Q[A] += (R - Q[A]) * weight_fn(N[A])
    R_log[A] += (R-R_log[A]) * (1 / N[A])
    avg_rew.append(average_reward(R_log, N))
    distance_to_true_q.append(np.linalg.norm(Q - q))
    if random_walk:
      q += 0.01 * np.random.randn(k)
  return Q, N, avg_rew, distance_to_true_q


def plot_average(arr, eps_list, n_bandits, y_lim, show=True):
  for i, eps in enumerate(eps_list):
    plt.plot(arr[i][1:] / n_bandits, label=f"eps={eps}")
  axes = plt.gca()
  axes.set_ylim(y_lim)
  plt.legend()
  if show:
    plt.show()


def plot_figures(k, n_bandits, n_steps, eps_list, weight_fn, random_walk,
                 y_bounds_1, y_bounds_2=None, Q_1=0, norm=False, show=True):
  avg_rew_per_eps = [np.zeros(n_steps) for _ in range(len(eps_list))]
  avg_rew_in_perc = [np.zeros(n_steps) for _ in range(len(eps_list))]
  distance_to_true_q = [np.zeros(n_steps) for _ in range(len(eps_list))]
  for i in range(n_bandits):
    print(i)
    bandit_pb = Bandit(k)
    for i, eps in enumerate(eps_list):
      Q, _, avg_rew, d = a_simple_bandit_algorithm(bandit_pb,
                                                   n_iterations=n_steps,
                                                   eps=eps,
                                                   weight_fn=weight_fn,
                                                   random_walk=random_walk,
                                                   Q_1=Q_1)
      avg_rew_per_eps[i] += avg_rew
      avg_rew_in_perc[i] += (avg_rew / bandit_pb.max_action)
      distance_to_true_q[i] += d
  plot_average(avg_rew_per_eps, eps_list, n_bandits, y_bounds_1, show=show)
  if y_bounds_2 is not None:
    plot_average(avg_rew_in_perc * 100, eps_list, n_bandits, y_bounds_2,
                 show=show)
  if norm:
    plot_average(distance_to_true_q, eps_list, n_bandits, [0, 10], show=show)


def main():
  # reproducing figure 2.2
  plot_figures(10, 2000, 1000, [0, 0.1, 0.01], sample_average, False, [0, 1.5],
               [0, 1])

  # # exercise 2.5
  plot_figures(10, 5, 10000, [0.1], sample_average, True, [0, 2])
  plot_figures(10, 5, 10000, [0.1], constant_alpha(alpha=0.1), True, [0, 3])

  # figure 2.3: optimistic greedy vs. realistic eps-greedy
  plot_figures(10, 2000, 1000, [0], constant_alpha(alpha=0.1), False, [0, 3],
               Q_1=5, show=False)
  plot_figures(10, 2000, 1000, [0.1], constant_alpha(alpha=0.1), False, [0, 3])


if __name__ == "__main__":
  main()