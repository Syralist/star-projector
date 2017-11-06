module dodecahedron(edge=10)
{
// Kantenlänge a
a = edge; //700;

// Umkreisradius ra
ra = (a/10)*sqrt(10*(5+sqrt(5)));

// Umkugelradius r
r = (a/4) * sqrt(6*(3+sqrt(5)));

// Winkel b1/2 aus Figure 3
beta1 = asin(ra/r);
beta2 = beta1 + 2 * asin(a/(2*r));

function foo(n, b) = [
	r * cos(n * 72) * sin(b),
	r * sin(n * 72) * sin(b),
	r * cos(b)
];

function bar(n, b) = [
	r * cos((n * 72)+36) * sin(b),
	r * sin((n * 72)+36) * sin(b),
	-r * cos(b)
];

points = [
	foo(0,beta1), foo(1,beta1), foo(2,beta1), foo(3,beta1), foo(4,beta1), 
	foo(0,beta2), foo(1,beta2), foo(2,beta2), foo(3,beta2), foo(4,beta2), 
	bar(0,beta1), bar(1,beta1), bar(2,beta1), bar(3,beta1), bar(4,beta1), 
	bar(0,beta2), bar(1,beta2), bar(2,beta2), bar(3,beta2), bar(4,beta2), 
];

paths=[
	// Deckel
	[0,3,2], [0,2,1], [0,4,3],
	// Oben 1
	[15,0,1], [15,1,6], [15,5,0],
	// Oben 2
	[16,1,2], [16,2,7], [16,6,1],
	// Oben 3
	[17,2,3], [17,3,8], [17,7,2],
	// Oben 4
	[18,3,4], [18,4,9], [18,8,3],
	// Oben 5
	[19,4,0], [19,0,5], [19,9,4],
	// Unten 1
	[5,10,14], [5,15,10], [5,14,19],
	// Unten 2
	[6,11,10], [6,16,11], [6,10,15],
	// Unten 3
	[7,12,11], [7,17,12], [7,11,16],
	// Unten 4
	[8,13,12], [8,18,13], [8,12,17],
	// Unten 5
	[9,14,13], [9,19,14], [9,13,18],
	// Boden
	[12,14,10], [12,10,11], [12,13,14]
];

polyhedron(points, paths);


// Debug: Zeichne alle Eckpunkte als kleine Würfel
//for(i=points) translate(i) cube([1,1,1], center = true);

// Debug: Zeichne Punkt Nr "x" als roten Würfel (Ändere x um anderen Punkt hervorzuheben...)
//for(i=[0:19]) if (i==9 /* hier das "x" ändern (0-19) */) #translate(points[i]) cube([1,1,1], center = true);
}

dodecahedron();