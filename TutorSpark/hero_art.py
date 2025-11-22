from __future__ import annotations

from typing import Dict, List, Tuple

# ---------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------

RESET = "\033[0m"

COLORS = {
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "green": "\033[32m",
    "magenta": "\033[35m",
    "white": "\033[37m",
    "grey": "\033[90m",
    "red": "\033[31m",
}


def _colorize_block(raw: str, palette: Dict[str, str]) -> List[str]:
    """
    Apply per-character colors based on a palette mapping, returning a list of
    colored lines (no width/height normalization here).
    """
    lines = raw.splitlines()
    colored: List[str] = []

    for line in lines:
        parts: List[str] = []
        for ch in line:
            color_name = palette.get(ch)
            if color_name:
                parts.append(COLORS[color_name] + ch + RESET)
            else:
                parts.append(ch)
        colored.append("".join(parts))
    return colored


def _pad_block(lines: List[str], width: int, height: int) -> List[str]:
    """
    Pad a list of lines with spaces so that:
      - each line is exactly `width` characters
      - number of lines is exactly `height`
    """
    padded = [line.ljust(width) for line in lines]
    if len(padded) < height:
        padded.extend([" " * width] * (height - len(padded)))
    return padded


# ---------------------------------------------------------
# RAW ASCII art for each class (uncolored)
# ---------------------------------------------------------

# MAGE – from ascii-art-4.txt (Black-mage style)  [oai_citation:1‡ascii-art-4.txt](sediment://file_0000000051ac722fa376f108c9e74686)
MAGE_RAW = r"""
                                                        
                                                        
                                      @@@@              
                                  @@@@+++~@@            
                                @@++++++rj@@            
                            @@@@+++++_rj@@              
                        @@@@++++++++rrrj@@              
            @@@@@@@@@@@@++++++++rrrrrr@@                
          Y@}+++++++++++++++rrrrrrrrrr@@                
            @@jrrrrrrr++++++++rrrrrrrr@@                
              @@@@@@xrrrrrrr++++++rx@@                  
                    @@@@@@rrrrrrrrrrrr@@                
                  @@++@@@@@@@@@@rrrrrrrj@@              
                @@@@++@@@@++@@@@@@@@rrrrrj@@            
              @@))@@@@@@@@++@@@@@@@@))@@rrrc@m          
            @@1)@@@@@@@@@@@@@@@@@@@@@@)1@@@@            
            @@1)))))@@@@@@)))))))))))))1@$              
            @@@@))))))))))))@@@@@@))))@@                
          Y@}+++@@))))))@@@@))))))))))){@@              
          Y@}+++@@))))@@@@@@))))))))))){@@              
            @@@@))))))++++@@))))))))))){@@              
            @@{)@@))))++++@@)))))))))))1@@              
            @@{)@@))))@@@@@@)))))))))1@@                
            @@{)))@@))))))))@@)))))))1@@                
            @@{)))))@@))))))@@)))))))1@@                
            @@{)))))))@@@@))))@@))))@@)1@@              
          Y@t)))))))))))))))))))@@@@))))){@@            
            @@@@@@@@@@@@@@@@@@@@    @@@@@@              
                                                        
                                                        
""".strip("\n")

# WARRIOR – blue armored fighter (from ascii-art-5.txt)
WARRIOR_RAW = r"""
                                                        
                                                        
                                 @                      
                              )$@@@@                    
                              ((@x@)(                   
                            ZxrjrYCCQkn                 
                           mxrrn<x(n0QQ$(               
                          )Qxnxx_c)QQQQM/(              
                         (pjk!@@$X$@@]@Q(               
                          dvk;;@I/]@]]@0                
                         (kna@;@*#W@]@@Q                
                        @@@xo@@@!@(@@@@C@@$(            
                     'rjxnnvkB;I!l[]hQQ$QQCCO@          
                    n.''`.'$(rrnrrrjrQj$]-]}]~i-k (     
                   ((;][]]}jnrjrrrxjrC0B([@i!rrjwC)$(   
                   ($I;I]](@xrrj@nn$jCQ$/@<rrrfQwmm|@   
                    !]|Q$   xxxjnBWxjCQ) @irjfxQQOm(@   
                 ((@@@@@    @JYQir{|ha@  @ijjjjnmmw(@   
                 ((I[[](   @Xxv@@>|@BQ0   rB!jjxmmC/@(  
                 c>$;l(B  @nnx@@@@@@@0QQ@   )$!~)*|(    
                 )k>r1B@)@nnvr@@@@@@@CCC0(              
             ()<`'~<$vx  $nnr@/@@@@@f$CC0f              
          (|B`';>0t)(    XxxnQ(  @   jxQQ@(             
        ($''><~a((      )JxnvQ       nxQQ@()            
      ml''<$)           )@@@@((      x@@@@@(            
     '<~))))          @@@@@@@        C@@@@@@@           
   )(   )                              (                
                                                        
                                                         
""".strip("\n")

# HEALER – dwarf healer with cross (from ascii-art-6.txt)
HEALER_RAW = r"""
                                                      
                                                      
                             >>>   > >   <<           
                          >>#zcccccczz////#>          
                         *Qczzzzzzz//zzzzzzc#         
                        >###c~~<zcc//zz~~~z##         
                       >#zO#(>>>#v.>>v#(>>>#z#*       
                      >hzzO#////|/o*a//////#zzXh      
     />>>>>>>##>     >>#z|jz|###|||||||###|z|zz#>>    
      |#z#zQbz/_f#  zzccz~1z~ cc<~jjj~~c..~c~cz#>>    
  >>  /##z>/M>X/cM>>M0zzz#0z~v~<~jjjjj~~nn~c#zX#>>    
  >>#_:..#>|#z####>>###c#czczccc/z~~~c/zccc###*>>     
   #_z{>(z_f##)#ab# >>>.#zzzc(zzc//czzc/#*>;_##>#     
   #/zf((z_f####### >, .##0z/czc(>cccc/#));vv#*>#>>   
     #z//_#t@@@@@@h#>>>##bbbb####zzzc//c##mmmmm#>>>+  
                     @i#>#ctz####bbbb##>..  #>>>>     
                      @B#/rcz/czz#####.>>>. ###>      
                     m#O#///c###>.>..>#...##z#*>      
                     m##O####I#*>..>>>#####)#>>>>     
                       #<>|#... .##>>#.....#>..#      
                       @@*#######>>>>>#######>>>>     
                     ( ZZZZZZZmmZZZZZZZZZZZZZZZZZi    
                                                      
                                                      
""".strip("\n")

# NEO PRO – Matrix-style hacker (from ascii-art-7.txt)
NEO_PRO_RAW = r"""
                                                      
                                                      
                           B0Qho                      
                       rhk$$@bW*M#|J                  
                       |*"^`]b[$B$jJ|                 
                        *:l;_d_1@^xz                  
                        t$W(@W+{z|t                   
                        /o(xi]#{Y$/j(                 
                       t/o'#1)}c(W0n1v                
                     p*@@@@MkCBmJW$r|Y                
                      #@W@@C#X$CXW@zZ/jnzcnvvn        
                    t|*0MBYBWb@Y0Z$kY0Qv1Xj)h         
                   xoXwBO/OaYY0vwCnvCw#Ca)O@$OJY      
                   jCCJ#X/oJ/OCcX0ZBB##YQ@BC@Cj0O     
                   fCC#YQCa00oJv*o$aM*$odBM$BbYJZ     
           0Jxftx  /m*@O0aJCCJzMkB@o$#MCB$$pMcvX0     
         )O0CYB1   rW#$OwJJWa$WJW$#o@o$0WppfQczC      
       pZZh>Y*#  xrQBW*XbYW@JBMQm@@b@BWkCQzwzdrXO     
      wOZhha*tfc0YhwMBCJZ#MMJW*mWMdaWBWhY$cZB$*xc     
   fXX+CO:,Bcf0bQZB$B@bZ$B$WZ$awkBWkW@  BOCBM#Zdr     
  fdZ"mQB[n]"0m@BpM$$aoWBadWk$a$B@$hW    pWYJBzb|     
  O"COptv$mMB$@@w@$@$bo*oYWpO$Ww$$WBM@   OW$B@dpQ     
       *)W#B$*h$h$$$pp0O*0kZaBBO*w@$h    $B#Q)B@W     
     IOchW    dBBB0BC0rMopMBhB$BQ@$$0     pYOJbpBp(   
    OMZ$     abBMW@W#p@CBCW$kBo$$Bp@BC      nZpJmmcv  
             BW$JbbOOM$X#Y@@CdaB$$Q@$#      ZkCCv#J   
                                                      
                                                      
""".strip("\n")

# ---------------------------------------------------------
# Per-class palettes (which chars get which colors)
# ---------------------------------------------------------

PALETTES: Dict[str, Dict[str, str]] = {
    "Mage": {
        "@": "yellow",   # hat / trim
        "+": "yellow",
        "~": "yellow",
        "r": "blue",
        "j": "blue",
        ")": "blue",
        "Y": "blue",
        "{": "blue",
        "t": "blue",
    },
    "Warrior": {
        "@": "blue",
        "$": "cyan",
        "Q": "cyan",
        "C": "cyan",
        "B": "cyan",
        "x": "white",
        "n": "white",
    },
    "Healer": {
        "#": "white",
        "z": "cyan",
        "c": "cyan",
        "b": "green",
        "m": "green",
        "Z": "green",
        "@": "yellow",   # holy highlight
        "+": "red",      # you can use '+' as cross color if you add it
    },
    "NEO PRO": {
        "@": "green",
        "$": "green",
        "B": "green",
        "W": "green",
        "0": "green",
        "1": "green",
        "O": "green",
        "C": "green",
    },
}

RAW_ART: Dict[str, str] = {
    "Mage": MAGE_RAW,
    "Warrior": WARRIOR_RAW,
    "Healer": HEALER_RAW,
    "NEO PRO": NEO_PRO_RAW,
}


def _build_normalized_art() -> Tuple[Dict[str, List[str]], int, int]:
    """
    Colorize and pad all hero sprites to a common size.

    Returns:
        (normalized_art, max_width, max_height)
    """
    max_width = 0
    max_height = 0
    split_cache: Dict[str, List[str]] = {}

    # First pass – determine max dimensions
    for cls, raw in RAW_ART.items():
        lines = raw.splitlines()
        split_cache[cls] = lines
        max_height = max(max_height, len(lines))
        max_width = max(max_width, max((len(l) for l in lines), default=0))

    # Second pass – colorize and pad to common W×H
    normalized: Dict[str, List[str]] = {}
    for cls, lines in split_cache.items():
        palette = PALETTES.get(cls, {})
        colored_lines = _colorize_block("\n".join(lines), palette)
        padded_lines = _pad_block(colored_lines, max_width, max_height)
        normalized[cls] = padded_lines

    return normalized, max_width, max_height


_NORMALIZED_ART, MAX_WIDTH, MAX_HEIGHT = _build_normalized_art()


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------

def get_hero_art(hero_class: str) -> str:
    """
    Return the colored ASCII art for the given hero class as a single string.

    Valid values (case-insensitive):
        'Mage', 'Warrior', 'Healer', 'NEO PRO'
    """
    key = hero_class.strip().upper()
    if key == "MAGE":
        cls = "Mage"
    elif key == "WARRIOR":
        cls = "Warrior"
    elif key == "HEALER":
        cls = "Healer"
    elif key in ("NEO", "NEO PRO", "NEOPRO"):
        cls = "NEO PRO"
    else:
        cls = "Mage"  # safe default

    lines = _NORMALIZED_ART[cls]
    return "\n".join(lines)


def print_hero_art(hero_class: str) -> None:
    """Convenience wrapper to print a hero sprite directly."""
    print(get_hero_art(hero_class))
