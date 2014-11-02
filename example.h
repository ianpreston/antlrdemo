set value -100;
set step -1;

loop:
    display value;
    exec sub value value step;
    exec le cond value 0;
    jumpif cond loop;

display "Done";
