class Main inherits IO{
    a : Ackermann ;
    main(): SELF_TYPE {{
        a <- new Ackermann;
        out_int(a.ackermann(1,3));
        }
    };
};

class Fact {
    fact(n : AUTO_TYPE): AUTO_TYPE{
        if (n=0) then 1 else n*fact(n-1) fi
    };
};

class Ackermann {
    ackermann(m:AUTO_TYPE, n: AUTO_TYPE): AUTO_TYPE{
        if (m = 0 ) then n+1 else
            if ( n = 0) then ackermann(m-1, 1) else
                ackermann(m-1, ackermann(m, n-1))
            fi
        fi
    };
};