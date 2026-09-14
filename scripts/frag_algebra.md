@@QUESTIONS@@
### Question 6 (Multiple Choice: Linear Inequalities)
What is the solution set to the inequality $-2x + 5 \ge 11$?

- **A)** $x \ge -3$
- **B)** $x > -3$
- **C)** $x \ge 3$
- **D)** $x \le -3$

---

### Question 7 (Multiple Choice: Parallel Lines)
Line $\ell$ is defined by $y = 3x - 7$. Which of the following is the equation of a line parallel to $\ell$ that passes through the point $(2, 1)$?

- **A)** $y = 3x - 7$
- **B)** $y = -3x + 5$
- **C)** $y = 3x - 5$
- **D)** $y = 3x + 1$

---

### Question 8 (Multiple Choice: Function Evaluation)
If $f(t) = 2t^2 - 5t + 3$, what is the value of $f(-2)$?

- **A)** $1$
- **B)** $9$
- **C)** $5$
- **D)** $21$

---

### Question 9 (Multiple Choice: Absolute Value Equations)
If $|2x - 3| = 7$, what is the greatest possible value of $x$?

- **A)** $-2$
- **B)** $5$
- **C)** $\frac{7}{2}$
- **D)** $2$

---

### Question 10 (Multiple Choice: Systems with No Solution)
In the system below, $k$ is a constant.

$$\begin{cases}
5x + ky = 9 \\
15x + 12y = 30
\end{cases}$$

For which value of $k$ does the system have no solution?

- **A)** $3$
- **B)** $12$
- **C)** $9$
- **D)** $4$

---

### Question 11 (Multiple Choice: Vieta's Formulas)
If $r_1$ and $r_2$ are the roots of $x^2 - 7x + 12 = 0$, what is the value of $r_1^2 + r_2^2$?

- **A)** $25$
- **B)** $49$
- **C)** $24$
- **D)** $73$

---

### Question 12 (Student-Produced Response: Linear Equations)
If $4(x - 3) + 7 = 5x - 2$, what is the value of $x$?

*(Enter your answer as an integer.)*

---

@@KEYS@@
| **Q6** | **D ($x \le -3$)** | Algebra: Linear Inequalities | Medium |
| **Q7** | **C ($y = 3x - 5$)** | Algebra: Parallel Lines | Medium |
| **Q8** | **D ($21$)** | Algebra: Function Evaluation | Medium |
| **Q9** | **B ($5$)** | Algebra: Absolute Value Equations | Medium |
| **Q10** | **D ($k = 4$)** | Algebra: Systems with No Solution | Hard |
| **Q11** | **A ($25$)** | Algebra: Vieta Sum of Squares | Hard |
| **Q12** | **-3** | Algebra: Linear Equations (SPR) | Medium |
@@RAT@@
### Question 6
- **Correct Answer: D ($x \le -3$)**
- **Method 1 (Isolate with Sign Flip)**:
  $$-2x + 5 \ge 11 \implies -2x \ge 6$$
  Dividing by a negative number reverses the inequality:
  $$x \le \frac{6}{-2} = -3$$
- **Method 2 (Desmos Check)**: Graph `y = -2x + 5` and `y = 11`. The line sits on or above 11 exactly when $x \le -3$.
- **Distractor Analysis**:
  - **A ($x \ge -3$)**: Forgot to flip the inequality sign when dividing by $-2$.
  - **B ($x > -3$)**: Forgot the flip and dropped the equality.
  - **C ($x \ge 3$)**: Divided $6$ by $2$ and kept the sign — double error.

---

### Question 7
- **Correct Answer: C ($y = 3x - 5$)**
- **Method 1 (Point-Slope Form)**:
  Parallel lines share the slope $m = 3$. Through $(2, 1)$:
  $$y - 1 = 3(x - 2) \implies y = 3x - 5$$
- **Method 2 (Desmos Check)**: Plot $(2, 1)$ and each option; only C passes through the point with slope $3$.
- **Distractor Analysis**:
  - **A ($y = 3x - 7$)**: Reuses the original line instead of shifting it.
  - **B ($y = -3x + 5$)**: Flips the slope sign (perpendicular-style error).
  - **D ($y = 3x + 1$)**: Sign error solving $1 = 6 + b$.

---

### Question 8
- **Correct Answer: D ($21$)**
- **Method 1 (Direct Substitution)**:
  $$f(-2) = 2(-2)^2 - 5(-2) + 3 = 2(4) + 10 + 3 = 8 + 10 + 3 = 21$$
- **Distractor Analysis**:
  - **A ($1$)**: Sign slip on the middle term: $8 - 10 + 3$.
  - **B ($9$)**: Forgot to square: $2(-2) + 10 + 3$.
  - **C ($5$)**: Sign slip on the squared term: $-8 + 10 + 3$.

---

### Question 9
- **Correct Answer: B ($5$)**
- **Method 1 (Split into Two Cases)**:
  $$2x - 3 = 7 \implies x = 5 \qquad\text{or}\qquad 2x - 3 = -7 \implies x = -2$$
  The greatest possible value is $5$.
- **Distractor Analysis**:
  - **A ($-2$)**: The lesser root — answers the wrong extreme.
  - **C ($\frac{7}{2}$)**: Solved $2x = 7$, dropping the $-3$.
  - **D ($2$)**: Arithmetic slip combining cases.

---

### Question 10
- **Correct Answer: D ($k = 4$)**
- **Method 1 (Parallel-and-Distinct Test)**:
  No solution means identical slopes but different intercepts:
  $$\frac{5}{15} = \frac{k}{12} \implies \frac{1}{3} = \frac{k}{12} \implies k = 4$$
  Check the constants differ in ratio: $\frac{9}{30} = \frac{3}{10} \ne \frac{1}{3}$ — parallel and distinct, so zero solutions.
- **Method 2 (Desmos Slider)**: Graph both lines with a slider for $k$; they stay parallel and apart exactly at $k = 4$.
- **Distractor Analysis**:
  - **A ($3$)**: Used the $x$-coefficient ratio instead of matching slopes.
  - **B ($12$)**: Kept the $y$-coefficient instead of solving the proportion.
  - **C ($9$)**: Grabbed the constant term.

---

### Question 11
- **Correct Answer: A ($25$)**
- **Method 1 (Vieta's Identity)**:
  For $x^2 - 7x + 12 = 0$: $r_1 + r_2 = 7$, $r_1 r_2 = 12$.
  $$r_1^2 + r_2^2 = (r_1 + r_2)^2 - 2r_1 r_2 = 49 - 24 = 25$$
- **Method 2 (Solve and Square)**: Roots are $3$ and $4$; $3^2 + 4^2 = 9 + 16 = 25$.
- **Distractor Analysis**:
  - **B ($49$)**: Squared the sum but forgot to subtract $2r_1 r_2$.
  - **C ($24$)**: Doubled the product instead of using the identity.
  - **D ($73$)**: Added $2r_1 r_2$ instead of subtracting.

---

### Question 12
- **Correct Answer: -3**
- **Method 1 (Expand and Isolate)**:
  $$4(x - 3) + 7 = 5x - 2 \implies 4x - 12 + 7 = 5x - 2 \implies 4x - 5 = 5x - 2$$
  $$-5 + 2 = 5x - 4x \implies x = -3$$
- **Verification**: Left side $4(-6) + 7 = -17$; right side $5(-3) - 2 = -17$. ✓

---
@@OVERVIEW@@
- **Number of Items**: 12 Items (10 Multiple Choice, 2 Student-Produced Responses)
