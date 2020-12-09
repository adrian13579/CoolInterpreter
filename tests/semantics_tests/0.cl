class Main {
    x: AUTO_TYPE;

    main (): A {
        x <- new A
     };
    succ(n : AUTO_TYPE) : AUTO_TYPE { n + 1 };
};

class A inherits IO {
    methodA():  SELF_TYPE {
        out_string("Hello")
    };
};