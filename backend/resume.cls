\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{resume}[2024/06/05 Resume class]

% Define the class
\LoadClass{article}

% Set the font size and paper size
\RequirePackage[margin=1in]{geometry}
\RequirePackage{fontspec}
\setmainfont{Arial}

% Define a simple header
\def\header#1{\centerline{\large\bf #1}}

% Define section and subsection formatting
\renewcommand{\section}[1]{\vspace{2ex}\noindent{\large\bf #1}\vspace{1ex}}
\renewcommand{\subsection}[1]{\vspace{1ex}\noindent{\bf #1}\vspace{0.5ex}}

% Suppress section numbering
\setcounter{secnumdepth}{0}

% Set paragraph spacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{1ex}
