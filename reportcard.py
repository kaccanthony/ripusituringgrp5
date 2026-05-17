def grade(score):
    x = float(score)
    return "A" if x >= 90 else "B" if x >= 80 else "C" if x >= 70 else "D" if x >= 60 else "F"


def report(name, scores):
    if not scores:
        return f"Report Card for {name}\nNo subjects provided."

    items = list(scores.items()) if isinstance(scores, dict) else scores
    rows = [(sub, float(val), grade(val)) for sub, val in items]

    lines = ["+" + "=" * 38 + "+",
             f"| Report Card for {name:<22}|",
             "+" + "=" * 38 + "+",
             f"| {'Subject':<20} | {'Score':<5} | {'Grade':<5} |",
             "+" + "-" * 38 + "+"]

    total = 0
    for sub, val, grd in rows:
        total += val
        lines.append(f"| {sub:<20} | {val:>5.1f} | {grd:<5} |")

    avg = total / len(rows)
    lines += ["+" + "-" * 38 + "+",
              f"| {'Average':<20} | {avg:>5.1f} | {grade(avg):<5} |",
              "+" + "=" * 38 + "+"]
    return "\n".join(lines)


if __name__ == "__main__":
    data = {"Math": 92, "English": 87, "Science": 95, "History": 78, "Art": 84}
    print(report("Student Name", data))
