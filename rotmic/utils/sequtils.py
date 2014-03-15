## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 Raik Gruenberg

## This file is part of the rotmic project (https://github.com/graik/rotmic).
## rotmic is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.

## rotmic is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
## You should have received a copy of the GNU Affero General Public
## License along with rotmic. If not, see <http://www.gnu.org/licenses/>.

"""
General purpose sequence utility methods.
"""
import re
from Bio.Seq import Seq, translate
import os.path as osp

def isdna( seq ):
    """@return: True, if given sequence looks like a DNA sequence"""
    atgc = [ seq.upper().count( letter ) for letter in ['A','T','C','G'] ]
    return sum( atgc ) == len( seq )

def isaa( seq ):
    """@return: True, if given sequence looks not like DNA"""
    atgc = [ seq.upper().count( letter ) for letter in ['A','T','C','G'] ]
    return sum( atgc ) < len( seq )

def seqlen( seq ):
    """
    @return: int, nucleotide basepair length of given protein or DNA sequence
    """
    if not seq:
        return 0
    seq = cleanseq( seq )
    if isaa( seq ):
        return 3 * len( seq )
    return len( seq )

def seq2fasta(seq, width=60):
    """Transform sequence seq to fasta format"""
    r = ""

    for i in xrange(0,len(seq),width):            
        r += seq[i:i+width]

        if(i+width>=len(seq)):
            pass
        else:
            r += "\n"

    return r

def dna2prot( seq ):
    """Translate DNA sequence to protein sequence"""
    return translate( Seq(seq) ).tostring()

def dna2complement( seq ):
    """Convert DNA sequence to complement dna sequence"""
    return Seq.complement( Seq( str(seq) )).tostring()

def dna2revcomplement( seq ):
    """Convert DNA sequence to reverse complement dna sequence"""
    return Seq.reverse_complement( Seq( str(seq) )).tostring()


def cleanseq( seq ):
    """remove whitespace and line break characters, and capitalize sequence"""
    return re.sub('\s','', seq.upper())


def recenter_sequence( seq, recenter=0, start=0, stop=None ):
    """
    Move starting point of a (assumed) circular sequence by |recenter| to the 
    right.Example:: 
        recenter_sequence( AAAATTTTCCCC, 4 ) -> TTTTCCCCAAAA
    After re-centering, the sequence can be trimmed by providing a new start
    and stop position. Example::
        recenter_sequence( AAAATTTTCCCC, 4, start=2, stop=-2 ) -> TTCCCCAA
    @param recenter: int, new starting point relative to current one
    @param start: int, position after recentering from which 
    """
    seq = seq[recenter:] + seq[:recenter]
    stop = stop or len( seq )
    
    return seq[start:stop]

