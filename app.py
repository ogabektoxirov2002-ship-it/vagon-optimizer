import streamlit as st
from itertools import permutations, product
from math import factorial
import math
import time

st.set_page_config(page_title="Оптимизация подачи ",
                   page_icon="🚂", layout="centered")

st.title("🚂 Оптимизация подачи вагонов ")

# === Ввод ===
num_paths = st.number_input("Количество соединительных путей (i):", min_value=1, step=1)

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

st.write("")  
st.write(f"Всего фронтов: {len(front_data)} (номеруются 1..{len(front_data)})")

# === helper funcs ===
def B_for_order(order, n_list, tau_list):
    B = 0
    t = len(order)
    for k in range(t):
        cum = sum(tau_list[j] for j in order[k:])
        B += n_list[order[k]] * cum
    return B

def smith_order_indices(indices, n_list, tau_list):
    return sorted(indices, key=lambda i: (tau_list[i] / n_list[i], i))

# === оценка количества комбинаций ===
i = len(paths_fronts)
p_list = [len(lst) for lst in paths_fronts]
t = sum(p_list)
K_exact = factorial(i) * math.prod(factorial(p) for p in p_list)

# === Оценка времени ===
approx_time = K_exact / 200000  # эмпирически: 200k комбин. ≈ 1 секунда
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

# увеличенный порог
THRESHOLD = 10_000_000

if st.button("🚀 Запустить расчёт"):
    n_list = [fd[0] for fd in front_data]
    tau_list = [fd[1] for fd in front_data]

    if K_exact > THRESHOLD:
        st.warning(f"K = {K_exact:,} превышает порог {THRESHOLD:,}. "
                   "Включён ускорённый режим (i! комбинаций, внутренний порядок — по правилу Смита).")
        path_indices = list(range(i))
        bestB = float("inf")
        best_order = None

        with st.spinner(f"Вычисляю ускорённый вариант... Пожалуйста, подождите."):
            start = time.time()
            for path_perm in permutations(path_indices):
                final_order = []
                for pidx in path_perm:
                    final_order.extend(smith_order_indices(paths_fronts[pidx], n_list, tau_list))
                curB = B_for_order(final_order, n_list, tau_list)
                if curB < bestB:
                    bestB = curB
                    best_order = final_order.copy()
            duration = time.time() - start

        st.success(f"Готово за {duration:.1f} сек.")
        st.write(f"Лучший B (ускорённый режим): {bestB:.3f}")
        st.write("Порядок фронтов (глобальные номера):", [x+1 for x in best_order])

    else:
        st.info(f"Полный перебор {K_exact:,} комбинаций. Это может занять до {msg_time}.")
        n_list = [fd[0] for fd in front_data]
        tau_list = [fd[1] for fd in front_data]
        path_indices = list(range(i))

        # подготавливаем все внутренние перестановки
        perm_lists = [list(permutations(paths_fronts[pidx])) for pidx in path_indices]

        bestB = float("inf")
        best_order = None
        total_checked = 0

        with st.spinner(f"Вычисляю {K_exact:,} комбинаций... Пожалуйста, подождите."):
            start = time.time()
            for path_perm in permutations(path_indices):
                for combo in product(*perm_lists):
                    final_order = []
                    for pidx in path_perm:
                        final_order.extend(combo[pidx])
                    curB = B_for_order(final_order, n_list, tau_list)
                    total_checked += 1
                    if curB < bestB:
                        bestB = curB
                        best_order = final_order.copy()
            duration = time.time() - start

        st.success(f"Полный перебор завершён за {duration:.1f} сек.")
        st.write(f"Проверено комбинаций: {total_checked:,}")
        st.write(f"Минимальный B = {bestB:.3f}")
        st.write("Оптимальный порядок фронтов (глобальные номера):", [x+1 for x in best_order])

st.caption("💡 Примечание: если расчёт занимает много времени, можно увеличить порог или использовать ускорённый режим.")

