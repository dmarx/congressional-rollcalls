-- Let's simplify this database to make it so we can just dump records directly
-- into it. We can ETL from this database into a more organized schema afterwards.
-- Let's start by slicing up each key that I populate for a particular role call

CREATE TABLE rollcalls
    (rollcall_id    NUMBER -- input
    ,year           NUMBER -- input
    ,description    TEXT   -- key
    ,issue          TEXT   -- key
    ,question       TEXT   -- key
    ,date           TEXT   -- key
    );

-- key:'votes' + inputs params for rollcall and year
CREATE TABLE rollcall_votes
    (rollcall_id    NUMBER  -- input
    ,year           NUMBER  -- input
    ,name_id        TEXT -- list value
    ,name           TEXT -- list value
    ,state          TEXT -- list value
    ,party          TEXT -- list value
    ,vote           TEXT -- list value
    );
    
CREATE TABLE issues
    (issue          TEXT -- key
    ,descr          TEXT -- key
    ,sponsor        TEXT -- key
    );

-- Subjects should be stored in a DIM table to reduce space. 
-- Doesn't really matter, this is going to be a small DB anyway.
CREATE TABLE issue_subjects
    (issue          TEXT -- key
    ,subject        TEXT -- list value
    );