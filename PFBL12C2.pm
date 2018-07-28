package Demeter::Plugins::PFBL12C2;  # -*- cperl -*-

use Moose;
use YAML;
extends 'Demeter::Plugins::FileType';

has '+is_binary'   => (default => 0);
has '+description' => (default => 'Photon Factory and SPring8 XAS Beamlines');
has '+version'     => (default => 0.3);
has 'nelements'    => (is => 'rw', isa => 'Int', default => 3);
has 'facility'     => (is => 'rw', isa => 'Str', default => 'KEK-PF');

use Demeter::Constants qw($PI);
use Const::Fast;
const my $HC      => 12398.52;	# slightly different than in D::C
#const my $HBARC   => 1973.27053324;
#const my $TWODONE => 6.2712;	# Si(111)
#const my $TWODTHR => 3.275;	# Si(311)

sub is {
  my ($self) = @_;
  open D, $self->file or $self->Croak("could not open " . $self->file . " as data (Photon Factory/SPring8/SAGALS)\n");
  my $line = <D>;
  close D;
  return 1 if ($line =~ m{9809\s+(?:KEK-PF|SPring-8|SAGA-LS)\s+(?:(BL\d+)|(NW\d+)|(\d+\w+\d*))});
  return 0;
};

sub fix {
  my ($self) = @_;
  
  # Load Deadt.d
  my $deadt = YAML::LoadFile("C:\\strawberry\\perl\\site\\lib\\Demeter\\Plugins\\PFBL12C2.conf");
  
  my $file = $self->file;
  my $new = File::Spec->catfile($self->stash_folder, $self->filename);
  ($new = File::Spec->catfile($self->stash_folder, "toss")) if (length($new) > 127);
  open my $D, $file or die "could not open $file as data (fix in PFBL12C)\n";
  open my $N, ">".$new or die "could not write to $new (fix in PFBL12C)\n";

  my $header = 1; # Turn on header flag
  my $ddistance = 1; # Turn on ddistance flag
  my $is_mssd = 0; # MSSD flag
  my $ndch = 0; # number of detector
  my @detector_id;
  my $header_array;
  
  #my $ampdeadtime = 0.411 * (10.0 ** -6.0);
  #my $preampdeadtime = 0.89 * (10.0 ** -6.0);
  
  #my @offsets;
  while (<$D>) {
    next if ($_ =~ m{\A\s*\z}); # Ignore text lines
    last if ($_ =~ m{}); # Exit from while loop
    chomp;
    if ($header and ($_ =~ m{\A\s+offset}i)) {
      my $this = $_;
      #@offsets = split(" ", $this);
      print $N '# ', $_, $/;
      print $N '# --------------------------------------------------', $/;
      print $N $header_array, $/;
      $header = 0; # Turn off header flag
    } elsif ($header and ($_ =~ m{9809\s+(KEK-PF|SPring-8|SAGA-LS)\s+(?:(BL\d+)|(NW\d+)|(\d+\w+\d*))})) {
      $self->facility($1);
    } elsif ($header and ($_ =~ m{\A\s+mode}i)) {
      my $this = $_;
      @detector_id = split(/\s+/, $this);
      my $element_array = '';
      my $element_id = 0;
      my $sca_id = 0;
      my $icr_id = 0;
      my $dismiss = 0;
      # I0=1,I1=2,SCA=3,PZT=5,ICR=103,PREAMP=101
      foreach my $id (@detector_id) {
        if ($id eq "0") {
          if ($dismiss < 2) {
            $id = '';
            $dismiss = $dismiss + 1;
          } else {
            $sca_id = $sca_id + 1;
            $id = "DISABLED" . $sca_id;
          }
        } elsif ($id eq "1") {
          $id = "I0";
        } elsif ($id eq "2") {
          $id = "I1";
        } elsif ($id eq "3") {
          $sca_id = $sca_id + 1;
          $id = "SCA" . $sca_id;
        } elsif ($id eq "5") {
          $id = "PZT";
        } elsif ($id eq "103") {
          $icr_id = $icr_id + 1;
          $id = '';
        } elsif ($id =~ m{mode}i) {
          $id = '';
        } elsif ($id eq "105") {
          $id = "PZT";
        } elsif ($id eq "101") {
          $id = "RESET";
        } else {
          
        }
        $element_array = $element_array . "  " . $id;
      }
      $header_array = '# energy_requested   energy_attained  time' . $element_array;
    } elsif ($header) {
      my $this = $_;
      if ($this =~ m{d=\s+(\d\.\d+)\s+A}i) {
        $ddistance = $1*2; # Extract D spacing value
      };
      if ($this =~ m{NDCH\s+=(\d+)}i) {
        $ndch = $1; $self->nelements($ndch);
        if ($1 > 5) { $is_mssd = 1; };
      };
      print $N '# ', $_, $/;
    } else {
      if ($is_mssd) { 
        my @list = split(" ", $_);
        $list[0] = ($HC) / ($ddistance * sin($list[0] * $PI / 180)); # Convert configured crystal angle to energy
        $list[1] = ($HC) / ($ddistance * sin($list[1] * $PI / 180)); # Convert obtained crystal angle to energy
        $list[2] = $list[2]; # Aquisition time
        foreach my $i (3 .. (3 + $ndch - 2)) {
          # I0
          if ($i == 22) {
            if ($self->facility eq 'SPring-8') {
              $list[$i] = $list[$i]/$list[2];
            } else {
              $list[$i] = $list[$i];
            }
          } else {
          # 
            if ($self->facility eq 'SPring-8') {
              my $shapingtime = $deadt->{shapingtime};
              my $preampdeadtime = 10.0 ** -6.0 * $deadt->{PF}->{individual}->{preamp}[-3+$i];
              my $ampdeadtime = 10.0 ** -6.0 * $deadt->{PF}->{individual}->{amp}->{$shapingtime}->[-3+$i];
              $list[$i] = ($list[$i]/$list[2]) / ( 1 - ($list[$i+$ndch]/$list[2]) * ($ampdeadtime + $preampdeadtime) );
            } else {
              my $shapingtime = $deadt->{shapingtime};
              my $preampdeadtime = 10.0 ** -6.0 * $deadt->{PF}->{individual}->{preamp}[-3+$i];
              my $ampdeadtime = 10.0 ** -6.0 * $deadt->{PF}->{individual}->{amp}->{$shapingtime}->[-3+$i];
              $list[$i] = $list[$i] / ( 1 - $list[$i+$ndch] * ($ampdeadtime + $preampdeadtime) );
              #$list[$i] = $list[$i];
            }
          }
        };
        #$list[2+$ndch] = $list[2+$ndch]; # I0
        my $pattern = "  %9.3f  %9.3f  %6.2f" . "  %12.3f" x $ndch . $/;
        printf $N $pattern, @list;
      } else {
        my @list = split(" ", $_);
        $list[0] = ($HC) / ($ddistance * sin($list[0] * $PI / 180)); # Convert configured crystal angle to energy
        $list[1] = ($HC) / ($ddistance * sin($list[1] * $PI / 180)); # Convert obtained crystal angle to energy
        # What is this??
        my $ndet = $#list-2;
        foreach my $i (1..$ndet) {
          $list[2+$i] = $list[2+$i]; # - $offsets[2+$i];
        };
        # What is this??
        my $pattern = "  %9.3f  %9.3f  %6.2f" . "  %12.3f" x $ndet . $/;
        printf $N $pattern, @list;
      }
    };
  };
  close $N;
  close $D;
  $self->fixed($new);
  return $new;
};

sub suggest {
  my ($self, $which) = @_;
  $which ||= 'transmission';
  if ($self->nelements > 5) { $which = 'MSSD'; }
  if ($which eq 'transmission') {
    return (energy      => '$2',
            numerator   => '$4',
            denominator => '$5',
            ln          =>  1,);
  } elsif (($which eq 'MSSD') and ($self->facility eq 'KEK-PF')) {
    return (energy      => '$2',
            numerator   => '$4+$5+$6+$7+$8+$9+$10+$11+$12+$13+$14+$15+$16+$17+$18+$19+$20+$21+$22',
            denominator => '$23',
            ln          =>  0,);
  } elsif (($which eq 'MSSD') and ($self->facility eq 'SPring-8')) {
    return (energy      => '$2',
            numerator   => '$4+$5+$6+$7+$8+$9+$10+$11+$12+$13+$14+$15+$16+$17+$18+$19+$20+$21+$22',
            denominator => '$23',
            ln          =>  0,);
  } else {
    return ();
  };
};

__PACKAGE__->meta->make_immutable;
1;

=head1 NAME

Demeter::Plugin::PFBL12C - filetype plugin for 9809 format (Photon Factory, SPring-8, SAGA-LS)

=head1 VERSION

This documentation refers to Demeter version 0.9.10.

=head1 SYNOPSIS

This plugin converts data recorded as a function of mono angle to data
as a function of energy.

=head1 METHODS

=over 4

=item C<is>

This file is identified by the string "KEK-PF" or "SPring-8" followed
by the beamline number in the first line of the file.

=item C<fix>

Convert the wavelength array to energy using the formula

   data.energy = 2 * pi * hbarc / 2D * sin(data.angle)

where C<hbarc=1973.27053324> is the the value in eV*angstrom units and
D is the Si(111) plane spacing.

=back

=head1 REVISIONS

=over 4

=item 0.3

Yohéi added support for data from SPring8.

=item 0.2

Thanks to 上村洋平 (Yohéi Uemura) from the Photon Factory for helping
me to refine the C<is> method to work with multiple PF XAS beamlines.

=back

=head1 AUTHOR

  Bruce Ravel <bravel@bnl.gov>
  http://xafs.org/BruceRavel

=cut
