def square():
  global x, squ
  squ = x * x
x = 1
while x <= 10:
  square()
  print(squ)
  x = x + 1
