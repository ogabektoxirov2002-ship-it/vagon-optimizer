import streamlit as st
from itertools import permutations, product
from math import factorial
import math
import time

st.set_page_config(page_title="Оптимизация подачи вагонов", page_icon="🚂", layout="centered")

st.title("🚂 Оптимизация подачи вагонов несколькими маневровыми локомотивами")

# === Ввод ===
num_paths = st.number_input("Количество соединительных путей (i):", min_value=1, step=1)
num_loco = st.number_input("Количество маневровых локомотивов:", min_value=1, step=1)

paths_fronts = []   # список фронтов по каждому пути
front_data = []     # глобальный список фронтов
global_idx = 0

for path in range(1, num_paths + 1):
    p = st.number_input(f"Путь {path}: количество фронтов (p_{path})", min_value=1, step=1, key=f"p{path}")
    local_idxs = []
    for j in range(1, p + 1):
        n = st.number_input(f"  Фронт (глоб. {global_idx+1}) — число вагонов", min_value=1, step=1,
                            key=f"n_{path}_{j}")
        tau = st.number_input(f"  Фронт (глоб. {global_idx+1}) — время τ (часы)", min_value=0.0, step=0.1,
                              key=f"t_{path}_{j}")
        front_data.append((n, tau, path-1, j-1))
        local_idxs.append(global_idx)
        global_idx += 1
    paths_fronts.append(local_idxs)

st.write(f"Всего фронтов: {len(front_data)} (номеруются 1..{len(front_data)})")

# === функции ===
def B_for_order(order, n_list, tau_list):
    B = 0
    t = len(order)
    for k in range(t):
        cum = sum(tau_list[j] for j in order[k:])
        B += n_list[order[k]] * cum
    return B

def smith_order_indices(indices, n_list, tau_list):
    return sorted(indices, key=lambda i: (tau_list[i] / n_list[i], i))

def divide_indices(indices, m):
    """делит фронты между m локомотивами по очереди"""
    groups = [[] for _ in range(m)]
    for i, idx in enumerate(indices):
        groups[i % m].append(idx)
    return groups

# === оценка количества комбинаций ===
i = len(paths_fronts)
p_list = [len(lst) for lst in paths_fronts]
t = sum(p_list)
K_exact = factorial(i) * math.prod(factorial(p) for p in p_list)

approx_time = K_exact / 200000
if approx_time < 1:
    msg_time = "мгновенно (< 1 сек)"
elif approx_time < 10:
    msg_time = f"≈ {approx_time:.1f} сек"
elif approx_time < 60:
    msg_time = f"≈ {approx_time:.1f} сек (~{approx_time/60:.1f} мин)"
else:
    msg_time = f"≈ {approx_time/60:.1f} мин"

st.write(f"🔢 Оценка числа комбинаций: **K = i! × Π pₙ! = {K_exact:,}**")
st.write(f"⏱️ Оценка времени вычисления: {msg_time}")

THRESHOLD = 10_000_000

if st.button("🚀 Рассчитать оптимальный вариант"):
    n_list = [fd[0] for fd in front_data]
    tau_list = [fd[1] for fd in front_data]

    path_indices = list(range(i))
    bestB_single = float("inf")
    best_order_single = None

    # === вычисляем однолокомотивный вариант ===
    with st.spinner("Вычисляется оптимальный порядок при одном локомотиве..."):
        if K_exact > THRESHOLD:
            for path_perm in permutations(path_indices):
                final_order = []
                for pidx in path_perm:
                    final_order.extend(smith_order_indices(paths_fronts[pidx], n_list, tau_list))
                curB = B_for_order(final_order, n_list, tau_list)
                if curB < bestB_single:
                    bestB_single = curB
                    best_order_single = final_order.copy()
        else:
            perm_lists = [list(permutations(paths_fronts[pidx])) for pidx in path_indices]
            for path_perm in permutations(path_indices):
                for combo in product(*perm_lists):
                    final_order = []
                    for pidx in path_perm:
                        final_order.extend(combo[pidx])
                    curB = B_for_order(final_order, n_list, tau_list)
                    if curB < bestB_single:
                        bestB_single = curB
                        best_order_single = final_order.copy()

    st.subheader("📊 Однолокомотивный вариант:")
    st.write(f"Минимальный B₁ = {bestB_single:.3f}")
    st.write("Оптимальный порядок фронтов:", [x+1 for x in best_order_single])

    # === если >1 локомотива ===
    if num_loco > 1:
        with st.spinner(f"Оптимизация распределения между {num_loco} локомотивами..."):
            # сортируем фронты по критерию Smith и делим по локомотивам
            indices = smith_order_indices(list(range(t)), n_list, tau_list)
            groups = divide_indices(indices, num_loco)

            total_B = 0
            st.subheader(f"🚂 Распределение по {num_loco} локомотивам:")

            for loco in range(num_loco):
                group = groups[loco]
                order = smith_order_indices(group, n_list, tau_list)
                Bval = B_for_order(order, n_list, tau_list)
                total_B += Bval
                st.write(f"Локомотив {loco+1}: фронты { [i+1 for i in order] },  B = {Bval:.3f}")

            economy = bestB_single - total_B
            st.success(f"✅ Суммарные вагоно-часы (B): {total_B:.3f}")
            st.info(f"💰 Экономия по сравнению с одним локомотивом: {economy:.3f}")

    else:
        st.info("🔹 Используется один локомотив — многолокомотивный расчёт не требуется.")

st.caption("💡")
