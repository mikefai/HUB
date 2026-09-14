@@QUESTIONS@@
### Question 6 (Multiple Choice: Radical Equations)
If $\sqrt{2x + 4} = 6$, what is the value of $x$?

- **A)** $1$
- **B)** $20$
- **C)** $16$
- **D)** $32$

---

### Question 7 (Multiple Choice: Rational Exponents)
What is the value of $27^{\frac{2}{3}}$?

- **A)** $18$
- **B)** $6$
- **C)** $3$
- **D)** $9$

---

### Question 8 (Multiple Choice: Exponential Growth Models)
A wildlife reserve starts with $200$ deer. The population triples every $4$ years according to $P(t) = 200 \cdot 3^{\frac{t}{4}}$, where $t$ is years. What is the population after $12$ years?

- **A)** $5{,}400$
- **B)** $1{,}800$
- **C)** $2{,}400$
- **D)** $600$

---

### Question 9 (Multiple Choice: Factored Form & Zeros)
Which quadratic function has zeros at $x = -3$ and $x = 5$ and a leading coefficient of $2$?

- **A)** $f(x) = 2x^2 - 4x + 30$
- **B)** $f(x) = 2(x - 3)(x + 5)$
- **C)** $f(x) = 2x^2 - 4x - 30$
- **D)** $f(x) = x^2 - 2x - 15$

---

### Question 10 (Multiple Choice: Extraneous Solutions)
What is the solution set of $\sqrt{x + 5} = x - 1$?

- **A)** $\{-1, 4\}$
- **B)** $\{-1\}$
- **C)** $\{\}$ (no solution)
- **D)** $\{4\}$

---

### Question 11 (Multiple Choice: End Behavior)
Let $f(x) = -3x^4 + 5x^2 - 2x + 7$. As $x \to -\infty$, $f(x)$ approaches which value?

- **A)** $\infty$
- **B)** $-\infty$
- **C)** $0$
- **D)** $-3$

---

### Question 12 (Student-Produced Response: Quadratic-Linear System)
The graphs of $y = x^2 - 4x + 3$ and $y = 2x - 5$ intersect at two points. What is the smaller $x$-coordinate of the points of intersection?

*(Enter your answer as an integer.)*

---

@@KEYS@@
| **Q6** | **C ($16$)** | Advanced Math: Radical Equations | Medium |
| **Q7** | **D ($9$)** | Advanced Math: Rational Exponents | Medium-Hard |
| **Q8** | **A ($5{,}400$)** | Advanced Math: Exponential Growth | Medium |
| **Q9** | **C ($2x^2 - 4x - 30$)** | Advanced Math: Factored Form & Zeros | Hard |
| **Q10** | **D ($\{4\}$)** | Advanced Math: Extraneous Solutions | Hard |
| **Q11** | **B ($-\infty$)** | Advanced Math: End Behavior | Medium |
| **Q12** | **2** | Advanced Math: Nonlinear Systems (SPR) | Medium-Hard |
@@RAT@@
### Question 6
- **Correct Answer: C ($16$)**
- **Method 1 (Square Both Sides)**:
  $$\sqrt{2x + 4} = 6 \implies 2x + 4 = 36 \implies 2x = 32 \implies x = 16$$
- **Verification**: $\sqrt{2(16) + 4} = \sqrt{36} = 6$. ✓
- **Distractor Analysis**:
  - **A ($1$)**: Solved $2x + 4 = 6$ without squaring.
  - **B ($20$)**: Added instead of subtracting: $(36 + 4)/2$.
  - **D ($32$)**: Forgot to divide by $2$.

---

### Question 7
- **Correct Answer: D ($9$)**
- **Method 1 (Root First, Then Power)**:
  $$27^{\frac{2}{3}} = (\sqrt[3]{27})^2 = 3^2 = 9$$
- **Distractor Analysis**:
  - **A ($18$)**: Multiplied $27 \cdot \frac{2}{3}$ — treated the exponent as a multiplier.
  - **B ($6$)**: Doubled the cube root instead of squaring it.
  - **C ($3$)**: Stopped after taking the cube root.

---

### Question 8
- **Correct Answer: A ($5{,}400$)**
- **Method 1 (Count the Periods)**:
  $$\frac{12}{4} = 3 \text{ tripling periods} \implies 200 \cdot 3^3 = 200 \cdot 27 = 5{,}400$$
- **Distractor Analysis**:
  - **B ($1{,}800$)**: Used only $2$ periods ($3^2$).
  - **C ($2{,}400$)**: Added linearly instead of multiplying.
  - **D ($600$)**: Applied a single tripling.

---

### Question 9
- **Correct Answer: C ($f(x) = 2x^2 - 4x - 30$)**
- **Method 1 (Build from Zeros)**:
  Zeros at $-3$ and $5$ give factors $(x + 3)(x - 5)$; leading coefficient $2$ gives:
  $$f(x) = 2(x + 3)(x - 5) = 2(x^2 - 2x - 15) = 2x^2 - 4x - 30$$
- **Distractor Analysis**:
  - **A**: Sign error — expands with $+30$ instead of $-30$.
  - **B**: Flipped both factor signs (zeros would be $3$ and $-5$).
  - **D**: Correct zeros but leading coefficient $1$, not $2$.

---

### Question 10
- **Correct Answer: D ($\{4\}$)**
- **Method 1 (Solve, Then Verify — Extraneous Hunt)**:
  $$\sqrt{x + 5} = x - 1 \implies x + 5 = x^2 - 2x + 1 \implies x^2 - 3x - 4 = 0$$
  $$(x - 4)(x + 1) = 0 \implies x = 4 \text{ or } x = -1$$
  Check $x = 4$: $\sqrt{9} = 3 = 4 - 1$. ✓
  Check $x = -1$: $\sqrt{4} = 2 \ne -1 - 1 = -2$. ✗ Extraneous — discard.
- **Distractor Analysis**:
  - **A ($\{-1, 4\}$)**: Kept the extraneous root without verifying.
  - **B ($\{-1\}$)**: Kept only the extraneous root.
  - **C (no solution)**: Discarded the valid root along with the bad one.

---

### Question 11
- **Correct Answer: B ($-\infty$)**
- **Method 1 (Leading-Term Dominance)**:
  For large $|x|$, $-3x^4$ dominates. Even degree with a negative leading coefficient sends both ends to $-\infty$.
- **Distractor Analysis**:
  - **A ($\infty$)**: Ignored the negative leading sign.
  - **C ($0$)**: Confused end behavior with a horizontal asymptote.
  - **D ($-3$)**: Reported the leading coefficient instead of the limit.

---

### Question 12
- **Correct Answer: 2**
- **Method 1 (Set Equal and Factor)**:
  $$x^2 - 4x + 3 = 2x - 5 \implies x^2 - 6x + 8 = 0 \implies (x - 2)(x - 4) = 0$$
  Intersections at $x = 2$ and $x = 4$; the smaller is $2$.
- **Verification**: At $x = 2$: $y = 4 - 8 + 3 = -1$ and $y = 4 - 5 = -1$. ✓

---
@@OVERVIEW@@
- **Number of Items**: 12 Items (9 Multiple Choice, 3 Student-Produced Responses)
