# Design: Expense, Net Result, and Category Percentages

## 1. Goal

Show how total expenses and the net result compare with total income in
statistics. Show where income came from, how much of it each expense category
used, and how much of total spending that category represents.

## 2. Scope

Add percentages to the following rows in monthly, quarterly, yearly, and
custom-range statistics:

* Total expenses as a percentage of total income.
* The existing net result as a percentage of total income.
* Each income category total as a percentage of total income.
* Each expense category total as **both** a percentage of total income and a
  percentage of total expenses, whether spending is below, at, or above income.

Do not add percentages to per-day or per-month averages, investment categories,
or individual transactions. Keep the existing totals, averages, investment
handling, and statistics availability rules unchanged. No database or migration
changes are needed.

## 3. Calculation

Use the rounded period totals already used to display the summary:

* `expense_percentage = total_expense / total_income * 100`
* `net_result_percentage = net_result / total_income * 100`
* `category_share_of_income = category_total / total_income * 100` (income and expense categories)
* `category_share_of_expenses = category_total / total_expense * 100` (expense categories only)

Use totals from the same report as the category row. For a filtered custom
range, use only the dates and categories included in that report.

Without Investments categories, the net result remains `total_income - total_expense`.
With Investments categories, show two changes for the selected period on the same row:

* **Cash change** = income − expenses − investment deposits + withdrawals.
* **Cash + investments change** = cash change + deposits − withdrawals + market
  gains/losses. Transfers cancel, so this equals income − expenses + market gains/losses.

Neither figure includes opening balances. Both show their own percentage of
period income and use the negative-result styling independently. For example,
income 300, expenses 100, a deposit of 150 and a gain of 20 produce
`Cash change: 50 (16.67%), Cash + investments change: 220 (73.33%)`.

Round each percentage to two decimal places. Do not clamp values:

* Expenses may be greater than `100%`.
* The net result may be negative, and its percentage must retain the negative
  sign.

Handle each denominator independently. If it is zero, display `—` for that
share only. For example, with no income, Products can still show
`Products - 150 (— of income, 30% of expenses)`. A zero category amount
against a nonzero total is `0%`, not `—`.

## 4. Presentation

Append the percentage in parentheses to the total expense and net result
amounts, for example:

* `Total expenses: 1200 (120%)`
* `Net income: -200 (-20%)`

For a period with no income, display the unavailable marker instead, for
example `Total expenses: 50 (—)` and `Net income: -50 (—)`.

On each category total row, put the shares together in parentheses immediately
after the amount, before any existing averages. For income of 1,000 and
expenses of 500, example rows are:

* `Salary - 800 (80% of income)`
* `Products - 150 (15% of income, 30% of expenses)`
* `Travel - 50 (5% of income, 10% of expenses)`

Mark the **total expenses percentage** red when expenses reach or exceed
income. On an expense category row, mark only its **share of expenses** red
when it exceeds half of total expenses; exactly 50% is not a warning.
Compare the amounts before rounding the percentages for display. An
unavailable share (`—`) is never highlighted.

When the displayed net result is negative, show both its amount and its
defined percentage in red. This also applies to investment-adjusted results.
With zero income, only the negative amount is red; the `—` stays uncolored.

Rank income and expense categories by their nonzero totals for the period.
For totals of 0, 25, and 80, the least category is the one with 25. If all
totals are zero, show no most/least category. This does not remove zero rows
from the period's category breakdown.

Apply the same format in every statistics period view. Keep the existing
expense/net-result labels, amount formatting, and styling; the examples above
describe the value placement rather than requiring new label text.

## 5. Implementation Notes

* Reuse the already calculated total income and total expenses for each period.
* Reuse the existing net-result calculation so its displayed amount and
  percentage cannot disagree, including when Investments are present.
* Keep percentage formatting in the statistics presentation layer; these are
  derived values and are not persisted.
* Pass the report totals to `_format_category_total_value` in
  `Statistics/statistics.py` for both monthly and aggregate category lists.
  Keep the existing category order, amount styling, and averages. Translate
  the new share labels in English, Ukrainian, and Polish.

## 6. Tests

Add focused statistics tests covering:

1. Expenses below income produce a positive expense percentage and a positive
   net-result percentage.
2. Expenses above income produce an expense percentage greater than `100%`
   and a negative net-result amount and percentage.
3. Zero income displays the unavailable marker without raising a division
   error, both when expenses are zero and when they are nonzero.
4. With Investments present, the net-result percentage uses the same
   investment-adjusted net result shown in the existing net-result row.
5. Monthly, quarterly, yearly, and custom-range summaries use the same
   percentage behavior.
6. With income of 1,000 and expenses of 500, verify the Salary, Products, and
   Travel rows above, including the order of the shares. With income still
   1,000 but expenses of 2,000, Products at 1,200 shows
   `(120% of income, 60% of expenses)`; neither share is hidden or capped.
7. With no income, verify the expense share is still shown. With income but
   no spending, a zero expense row shows `(0% of income, — of expenses)`.
   In a filtered custom range, excluded categories do not affect either share.
8. Verify red styling below, at, and above each threshold: 100% triggers the
   total spending warning, but 50% does not trigger the category warning.
