import sys

class Rectangle:
    def __init__(self, length, height):
        self.length = length
        self.height = height

    def area(self):
        return self.length * self.height

    def perimeter(self):
        return 2 * (self.length + self.height)

def main():
    # Ensure two arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <length> <height>")
        return

    # Collect arguments and convert to float
    length = float(sys.argv[1])
    height = float(sys.argv[2])

    # Create Rectangle object
    rectangle = Rectangle(length, height)

    # Display area and perimeter
    print(f"Area of rectangle: {rectangle.area()}")
    print(f"Perimeter of rectangle: {rectangle.perimeter()}")

if __name__ == "__main__":
    main()
