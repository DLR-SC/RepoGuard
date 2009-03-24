# pylint: disable-msg=W0232, W0603, E1101

# Copyright 2008 German Aerospace Center (DLR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test methods for the Checkstyle class.
"""

from __future__ import with_statement

import os
import tempfile

from configobj import ConfigObj

from repoguard.checks import checkstyle
from repoguard.checks.checkstyle import Checkstyle, Config
from repoguard.testutil import TestRepository

config_string = """
java=C:/Programme/Java/jdk1.6.0_11/bin/java.exe
paths=C:/,
config_file=%CONFIGFILE%
"""

longJavaFile = """
////////////////////////////////////////////////////////////////////////////////
// checkstyle: Checks Java source code for adherence to a set of rules.
// Copyright (C) 2001-2007  Oliver Burn
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
////////////////////////////////////////////////////////////////////////////////
package com.puppycrawl.tools.checkstyle.checks.coding;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Stack;

import com.puppycrawl.tools.checkstyle.api.Check;
import com.puppycrawl.tools.checkstyle.api.DetailAST;
import com.puppycrawl.tools.checkstyle.api.ScopeUtils;
import com.puppycrawl.tools.checkstyle.api.TokenTypes;

/**
 * <p>
 * Ensures that local variables that never get their values changed,
 * must be declared final.
 * </p>
 * <p>
 * An example of how to configure the check is:
 * </p>
 * <pre>
 * &lt;module name="FinalLocalVariable"&gt;
 *     &lt;property name="token" value="VARIABLE_DEF"/&gt;
 * &lt;/module&gt;
 * </pre>
 * @author k_gibbs, r_auckenthaler
 */
public class FinalLocalVariableCheck extends Check
{
    /** Scope Stack */
    private final Stack mScopeStack = new Stack();

    /**
     * {@inheritDoc}
     */
    public int[] getDefaultTokens()
    {
        return new int[] {
            TokenTypes.IDENT,
            TokenTypes.CTOR_DEF,
            TokenTypes.METHOD_DEF,
            TokenTypes.VARIABLE_DEF,
            TokenTypes.INSTANCE_INIT,
            TokenTypes.STATIC_INIT,
            TokenTypes.LITERAL_FOR,
            TokenTypes.SLIST,
            TokenTypes.OBJBLOCK,
        };
    }

    /** {@inheritDoc} */
    public int[] getAcceptableTokens()
    {
        return new int[] {
            TokenTypes.VARIABLE_DEF,
            TokenTypes.PARAMETER_DEF,
        };
    }

    /** {@inheritDoc} */
    public int[] getRequiredTokens()
    {
        return new int[] {
            TokenTypes.IDENT,
            TokenTypes.CTOR_DEF,
            TokenTypes.METHOD_DEF,
            TokenTypes.INSTANCE_INIT,
            TokenTypes.STATIC_INIT,
            TokenTypes.LITERAL_FOR,
            TokenTypes.SLIST,
            TokenTypes.OBJBLOCK,
        };
    }

    /**
     * {@inheritDoc}
     */
    public void visitToken(DetailAST aAST)
    {
        switch(aAST.getType()) {
        case TokenTypes.OBJBLOCK:
        case TokenTypes.SLIST:
        case TokenTypes.LITERAL_FOR:
        case TokenTypes.METHOD_DEF:
        case TokenTypes.CTOR_DEF:
        case TokenTypes.STATIC_INIT:
        case TokenTypes.INSTANCE_INIT:
            mScopeStack.push(new HashMap());
            break;

        case TokenTypes.PARAMETER_DEF:
            if (ScopeUtils.inInterfaceBlock(aAST)
                || inAbstractMethod(aAST))
            {
                break;
            }
        case TokenTypes.VARIABLE_DEF:
            if ((aAST.getParent().getType() != TokenTypes.OBJBLOCK)
                && (aAST.getParent().getType() != TokenTypes.FOR_EACH_CLAUSE))
            {
                insertVariable(aAST);
            }
            break;

        case TokenTypes.IDENT:
            final int parentType = aAST.getParent().getType();
            if ((TokenTypes.POST_DEC        == parentType)
                || (TokenTypes.DEC          == parentType)
                || (TokenTypes.POST_INC     == parentType)
                || (TokenTypes.INC          == parentType)
                || (TokenTypes.ASSIGN       == parentType)
                || (TokenTypes.PLUS_ASSIGN  == parentType)
                || (TokenTypes.MINUS_ASSIGN == parentType)
                || (TokenTypes.DIV_ASSIGN   == parentType)
                || (TokenTypes.STAR_ASSIGN  == parentType)
                || (TokenTypes.MOD_ASSIGN   == parentType)
                || (TokenTypes.SR_ASSIGN    == parentType)
                || (TokenTypes.BSR_ASSIGN   == parentType)
                || (TokenTypes.SL_ASSIGN    == parentType)
                || (TokenTypes.BXOR_ASSIGN  == parentType)
                || (TokenTypes.BOR_ASSIGN   == parentType)
                || (TokenTypes.BAND_ASSIGN  == parentType))
            {
                if (aAST.getParent().getFirstChild() == aAST) {
                    removeVariable(aAST);
                }
            }
            break;

        default:
        }
    }

    /**
     * Determines whether an AST is a descentant of an abstract method.
     * @param aAST the AST to check.
     * @return true if aAST is a descentant of an abstract method.
     */
    private boolean inAbstractMethod(DetailAST aAST)
    {
        DetailAST parent = aAST.getParent();
        while (parent != null) {
            if (parent.getType() == TokenTypes.METHOD_DEF) {
                final DetailAST modifiers =
                    parent.findFirstToken(TokenTypes.MODIFIERS);
                return modifiers.branchContains(TokenTypes.ABSTRACT);
            }
            parent = parent.getParent();
        }
        return false;
    }

    /**
     * Inserts a variable at the topmost scope stack
     * @param aAST the variable to insert
     */
    private void insertVariable(DetailAST aAST)
    {
        if (!aAST.branchContains(TokenTypes.FINAL)) {
            final HashMap state = (HashMap) mScopeStack.peek();
            final DetailAST ast = aAST.findFirstToken(TokenTypes.IDENT);
            state.put(ast.getText(), ast);
        }
    }

    /**
     * Removes the variable from the Stacks
     * @param aAST Variable to remove
     */
    private void removeVariable(DetailAST aAST)
    {
        for (int i = mScopeStack.size() - 1; i >= 0; i--) {
            final HashMap state = (HashMap) mScopeStack.get(i);
            final Object obj = state.remove(aAST.getText());
            if (obj != null) {
                break;
            }
        }
    }

    /**
     * {@inheritDoc}
     */
    public void leaveToken(DetailAST aAST)
    {
        super.leaveToken(aAST);

        switch(aAST.getType()) {
        case TokenTypes.OBJBLOCK:
        case TokenTypes.SLIST:
        case TokenTypes.LITERAL_FOR:
        case TokenTypes.CTOR_DEF:
        case TokenTypes.STATIC_INIT:
        case TokenTypes.INSTANCE_INIT:
        case TokenTypes.METHOD_DEF:
            final HashMap state = (HashMap) mScopeStack.pop();
            final Iterator finalVars = state.values().iterator();

            while (finalVars.hasNext()) {
                final DetailAST var = (DetailAST) finalVars.next();
                log(var.getLineNo(), var.getColumnNo(),
                    "final.variable", var.getText());
            }
            break;

        default:
        }
    }
}"""

class TestCheckstyle:

    @classmethod
    def setup_class(cls):
        handle, filename = tempfile.mkstemp()
        with os.fdopen(handle, "w") as fd:
            fd.write('<?xml version="1.0"?>\n')
            fd.write('<!DOCTYPE module PUBLIC "-//Puppy Crawl//DTD Check Configuration 1.2//EN" ')
            fd.write('"http://www.puppycrawl.com/dtds/configuration_1_2.dtd">\n')
            fd.write('<module name="Checker">')
            fd.write('<module name="NewlineAtEndOfFile" />')
            fd.write('</module>')

        cls.config = ConfigObj(config_string.replace("%CONFIGFILE%", filename).splitlines())

    def test_for_success(self):
        repository = TestRepository()
        repository.add_file("Test.java", 'public class test { }\n')
        transaction = repository.commit()
        checkstyle = Checkstyle(transaction)
        assert checkstyle.run(self.config, debug=True).success == True

    def test_for_failure(self):
        repository = TestRepository()
        repository.add_file("Test.java", 'public class test { }')
        transaction = repository.commit()
        checkstyle = Checkstyle(transaction)
        assert checkstyle.run(self.config, debug=True).success == False
        
    def test_for_long_java_file(self):
        repository = TestRepository()
        repository.add_file("Test.java", longJavaFile)
        transaction = repository.commit()
        checkstyle = Checkstyle(transaction)
        assert checkstyle.run(self.config, debug=True).success == False
        
    def test_classpath(self):
        checkstyle.os.path.isdir = lambda path: path == '/libs'
        checkstyle.os.listdir = lambda path: ['foo.jar', 'bar.txt']
        config = Config()
        config.paths = ['/libs', '/path/dummy.jar']
        result = ":".join((
            os.path.normpath('/libs/foo.jar'), 
            os.path.normpath('/path/dummy.jar')
        ))
        assert config.classpath == result
